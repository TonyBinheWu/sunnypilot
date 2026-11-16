/* C4 factory-cache compatibility entry. Compile statically for aarch64.
 * The embedded pinned sunnypilot installer remains unmodified. No shell-built
 * Git commands, Params writes, cache deletion or network retry loop here. */
#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <unistd.h>

#ifndef DATA_ROOT
#define DATA_ROOT "/data"
#endif
#ifndef MODEL_PATH
#define MODEL_PATH "/sys/firmware/devicetree/base/model"
#endif
#define CHECKOUT DATA_ROOT "/openpilot"
#define CONTINUE DATA_ROOT "/continue.sh"
#define ORIGIN "https://github.com/TonyBinheWu/sunnypilot.git"
extern const unsigned char installer_payload[];
extern const size_t installer_size;

static int run(char *const args[]) {
  pid_t pid = fork();
  if (pid < 0) return -1;
  if (pid == 0) { execv(args[0], args); _exit(127); }
  int status;
  while (waitpid(pid, &status, 0) < 0) if (errno != EINTR) return -1;
  return WIFEXITED(status) ? WEXITSTATUS(status) : -1;
}

static int failure(const char *stage) {
  fprintf(stderr, "Carrot installation stopped: %s. Log: " DATA_ROOT "/carrot-installer.log\n", stage);
  FILE *out = fopen(DATA_ROOT "/carrot-installer-error.txt", "w");
  if (out) { fprintf(out, "%s\n", stage); fclose(out); }
  return 1;
}

int main(void) {
  char model[128] = {0};
  FILE *in = fopen(MODEL_PATH, "rb");
  if (!in) return failure("device_model_unavailable");
  (void)fread(model, 1, sizeof(model)-1, in); fclose(in);
  for (size_t i=0; i<sizeof(model); ++i) if (model[i]>='A' && model[i]<='Z') model[i]+='a'-'A';
  if (!strstr(model, "mici") && !strstr(model, "c4")) return failure("C4_installer_required");
  int logfd = open(DATA_ROOT "/carrot-installer.log", O_CREAT|O_WRONLY|O_APPEND, 0600);
  if (logfd < 0) return failure("log_unavailable");
  if (dup2(logfd, STDOUT_FILENO)<0 || dup2(logfd, STDERR_FILENO)<0) { close(logfd); return failure("log_redirect"); }
  close(logfd);
  setvbuf(stdout, NULL, _IONBF, 0);
  puts("Carrot C4 installer v1: checking factory-cache origin");
  // Only a marked factory cache before handoff is eligible. Existing installed
  // software is never retargeted by this compatibility preflight.
  if (access(CONTINUE, F_OK) != 0 && access(DATA_ROOT "/.openpilot_cache", F_OK) == 0 && access(CHECKOUT "/.git", F_OK) == 0) {
    char *args[] = {"/usr/bin/git", "-C", CHECKOUT, "remote", "set-url", "origin", ORIGIN, NULL};
    if (run(args) != 0) return failure("factory_cache_origin_failed");
    puts("Factory cache now uses the requested sunnypilot repository");
  }
  char path[] = "/tmp/carrot-installer-XXXXXX";
  int fd = mkstemp(path);
  if (fd < 0) return failure("temporary_file_failed");
  size_t offset=0;
  while (offset<installer_size) {
    ssize_t n=write(fd, installer_payload+offset, installer_size-offset);
    if (n<0 && errno==EINTR) continue;
    if (n<=0) { close(fd); unlink(path); return failure("payload_write_failed"); }
    offset+=(size_t)n;
  }
  int ready = fchmod(fd,0700)==0 && fsync(fd)==0;
  if (close(fd)!=0) ready=0;
  if (!ready) { unlink(path); return failure("payload_sync_failed"); }
  char *args[] = {path, NULL};
  int result=run(args);
  unlink(path);
  if (result!=0) return failure("installer_process_failed");
  fd=open(CONTINUE,O_RDONLY);
  if (fd<0) return failure("handoff_missing");
  struct stat st;
  int durable=fstat(fd,&st)==0 && S_ISREG(st.st_mode) && st.st_size>0 && (st.st_mode&0111) && fsync(fd)==0;
  if(close(fd)!=0) durable=0;
  fd=open(DATA_ROOT,O_RDONLY|O_DIRECTORY);
  if(fd<0) durable=0;
  else { if(fsync(fd)!=0) durable=0; close(fd); }
  if(!durable) return failure("handoff_invalid_or_not_durable");
  unlink(DATA_ROOT "/carrot-installer-error.txt");
  puts("Installation handoff verified and synced");
  return 0;
}
