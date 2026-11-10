# FormosaLink: IIS / Python deployment

GitHub OAuth / [MULTI_USER.md](MULTI_USER.md)

Origin: `https://formosapilot.dinglu-t.com`. File destination: `\\192.168.20.145\htdocs\FormosaPilot`.
Use a dedicated IIS site at the origin root, not a virtual subdirectory. SMB access uploads files; it does not execute server setup.

If script execution is disabled, use a process-only policy: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File "\\192.168.20.145\htdocs\FormosaPilot\App_Data\setup-server.ps1" -Language en`. Add `-InstallPython` if the existing interpreter is unsupported. It installs a SHA-256-pinned, PSF-signature-verified official Python 3.14.10 NuGet runtime into a private directory outside the website, without altering PATH, existing Python or launcher registration. No permanent execution policy is changed.

Automatic setup: on the IIS host, open administrator PowerShell and run `& '\\192.168.20.145\htdocs\FormosaPilot\App_Data\setup-server.ps1' -Language en`. It discovers the local share path, validates Python 3.12–3.14, installs dependencies in an isolated venv, prompts for the password locally if needed, copies runtime code outside the web root and registers a LocalService startup task with retries and rotating logs. Use a system Python installation readable by LocalService. Existing credentials are preserved. `-CheckOnly` inspects without installing; `-Python 'C:\Python312\python.exe'` selects an interpreter. It does not enable remote management, open firewall ports or alter global IIS settings. After setup, return to the chat for external validation. The manual alternative follows.

1. Configure DNS, port 443 and a valid TLS certificate. Install IIS Static Content, WebSocket Protocol, URL Rewrite and ARR. Enable ARR proxy and `preserveHostHeader=true` at server level, with a timeout of at least 60 seconds and WebSocket Upgrade forwarding. Keep Python bound to `127.0.0.1:8765`. PHP is not required. Give IIS read access to the site, including UNC/NTFS permissions where applicable.
2. From the repository root, run `tools/deploy/publish_formosalink_iis.ps1 -CheckOnly`, then run it without `-CheckOnly`. Initial destination must be empty; subsequent deployment uses its marker. The script verifies file hashes and never copies runtime secrets. Restart Python after updating its source.
3. On the IIS server, locate the actual local directory behind the share. The following `D:\htdocs\FormosaPilot` is an example, not a verified drive path:

```powershell
$siteRoot = 'D:\htdocs\FormosaPilot'
$dataRoot = 'C:\ProgramData\FormosaLink'
Set-Location "$siteRoot\App_Data\server-package"
py -3.12 -m venv C:\ProgramData\FormosaLink-venv
$python = 'C:\ProgramData\FormosaLink-venv\Scripts\python.exe'
& $python -m pip install -r formosalink\requirements.txt
& $python -m formosalink.server.config --data-dir $dataRoot --origin https://formosapilot.dinglu-t.com --lang en
& "$siteRoot\App_Data\start-server.ps1" -DataDirectory $dataRoot -Python $python
```

Enter a password of at least 14 characters at the prompt. Keep the data directory outside the web root and on a local disk, not SMB. Restrict Windows ACLs to the backend identity and administrators; POSIX file modes do not establish Windows ACLs. Initialization refuses to overwrite an existing config. Use one worker. After foreground validation, create a Windows Task Scheduler startup task running the launcher with the same arguments, regardless of interactive login, with restart-on-failure and no parallel instances. Its account needs source read and state-directory write permissions.

4. Install/build this change on the device, then pair locally while parked:

```bash
python -m openpilot.sunnypilot.formosalink.cli --lang en pair --url https://formosapilot.dinglu-t.com --enable
python -m openpilot.sunnypilot.formosalink.cli --lang en status
```

Sign in on your phone and enter the one-use 12-character code and full 24-character fingerprint within ten minutes. The optional manager process starts after local enablement. Identity is stored at `/data/formosalink/identity.json`, mode 0600, independently of comma/sunnylink. Never clone it or include it in ordinary configuration backups. Revoke permanently disables that identity. To re-pair, locally disable the agent, secure/archive and move the old identity, then create a new one. Disable with `python -m openpilot.sunnypilot.formosalink.cli --lang en disable`.

5. Verify HTTPS health, unauthorized device API returning 401, blocked App_Data/Python/secret downloads, pairing over mobile internet, all three UI languages and home-screen installation. Disconnect the device: it must show offline/stale. Invalid or >20-second samples must not appear live. Revoke access and verify immediate disconnection and rejected reconnects. Test both C3X/C4 and both maintained branches for process lifecycle, source validity and resource use. Turning off the cloud must not gate driving processes.

Stop Python before backing up the entire protected data directory. Restore config and SQLite together, restart, and allow devices to reconnect. Lost registries require re-pairing. A 500.19 response generally means a missing/locked IIS module or configuration; resolve that instead of removing download protection. Preserve the original Host in ARR or the backend will return 400. SMB file publication alone does not verify TLS, IIS, process startup or external reachability.

For local development, initialize a separate directory with `--origin http://127.0.0.1:8765`, then run `python -m formosalink.server --data-dir <directory>`. The server serves the dashboard directly. An explicit CLI `--state-dir <demo-directory>` with `pair` and then `run --demo` sends labelled simulation; no demo data is enabled by default.

Optional Linux: initialize with `docker compose -f formosalink/deploy/compose.yaml run --rm -it formosalink python -m formosalink.server.config --data-dir /state --origin https://formosapilot.dinglu-t.com`, then `up -d`. Provide a host TLS reverse proxy. This skeleton uses Linux host networking, not Windows Docker.
