/* C4 factory-cache compatibility entry. Compile statically for aarch64.
 * The embedded pinned sunnypilot installer remains unmodified. No shell-built
 * Git commands, Params writes, cache deletion or network retry loop here. */
#define _GNU_SOURCE
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
extern const unsigned char installer_payload[];
extern const size_t installer_size;
static char cache_backup[]=DATA_ROOT "/.carrot-factory-cache-XXXXXX";
static int cache_hidden=0;

static void restore_cache_marker(void) {
  if (!cache_hidden) return;
  // Never overwrite a concurrently created marker. Preserve the parked file
  // if the cache disappeared or another actor changed its state.
  if (access(CHECKOUT "/.git",F_OK)==0 && renameat2(AT_FDCWD,cache_backup,AT_FDCWD,DATA_ROOT "/.openpilot_cache",RENAME_NOREPLACE)==0) {
    cache_hidden=0;
  } else fprintf(stderr,"Factory marker retained at %s; not overwriting current state\n",cache_backup);
}

static int run(char *const args[]) {
  pid_t pid = fork();
  if (pid < 0) return -1;
  if (pid == 0) { execv(args[0], args); perror("installer exec failed"); _exit(127); }
  int status;
  while (waitpid(pid, &status, 0) < 0) if (errno != EINTR) return -1;
  if (WIFSIGNALED(status)) fprintf(stderr,"Installer child signal: %d\n",WTERMSIG(status));
  if (WIFEXITED(status)) fprintf(stderr,"Installer child exit: %d\n",WEXITSTATUS(status));
  return WIFEXITED(status) ? WEXITSTATUS(status) : -1;
}

static int failure(const char *stage) {
  int saved_errno=errno;
  restore_cache_marker();
  fprintf(stderr, "Carrot installation stopped: %s (errno %d). Log: " DATA_ROOT "/carrot-installer.log\n", stage,saved_errno);
  FILE *out = fopen(DATA_ROOT "/carrot-installer-error.txt", "w");
  if (out) { fprintf(out, "%s\n", stage); fclose(out); }
  return 1;
}

int main(void) {
  int logfd = open(DATA_ROOT "/carrot-installer.log", O_CREAT|O_WRONLY|O_APPEND, 0600);
  if (logfd < 0) return failure("log_unavailable");
  if (dup2(logfd, STDOUT_FILENO)<0 || dup2(logfd, STDERR_FILENO)<0) { close(logfd); return failure("log_redirect"); }
  close(logfd);
  setvbuf(stdout, NULL, _IONBF, 0);
  printf("Carrot C4 installer v2: starting, uid=%ld\n",(long)getuid());
  char model[128] = {0};
  FILE *in = fopen(MODEL_PATH, "rb");
  if (!in) return failure("device_model_unavailable");
  size_t read_size=fread(model, 1, sizeof(model)-1, in);
  int model_ok=read_size>0 && !ferror(in);
  if (fclose(in)!=0 || !model_ok) return failure("device_model_unavailable");
  for (size_t i=0; i<sizeof(model); ++i) if (model[i]>='A' && model[i]<='Z') model[i]+='a'-'A';
  if (!strstr(model, "mici") && !strstr(model, "c4")) return failure("C4_installer_required");
  // Factory caches can be read-only or owned by root. Do not run Git or change
  // their config. Park only the marker so the original installer fresh-clones.
  if (access(CONTINUE, F_OK) != 0 && access(DATA_ROOT "/.openpilot_cache", F_OK) == 0 && access(CHECKOUT "/.git", F_OK) == 0) {
    struct stat marker;
    if (lstat(DATA_ROOT "/.openpilot_cache",&marker)!=0 || !S_ISREG(marker.st_mode)) return failure("factory_marker_invalid");
    int reserve=mkstemp(cache_backup);
    if (reserve<0) return failure("factory_marker_backup_failed");
    if (close(reserve)!=0) { unlink(cache_backup); return failure("factory_marker_backup_failed"); }
    if (rename(DATA_ROOT "/.openpilot_cache",cache_backup)!=0) { unlink(cache_backup); return failure("factory_marker_park_failed"); }
    cache_hidden=1;
    puts("Factory cache preserved; using fresh clone without writing its Git config");
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
  if(cache_hidden) { unlink(cache_backup); cache_hidden=0; }
  unlink(DATA_ROOT "/carrot-installer-error.txt");
  puts("Installation handoff verified and synced");
  return 0;
}
