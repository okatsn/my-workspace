# Ubuntu Quick Setup Cheat Sheet

Concise steps to tune input, UI, dev tools, and basic security. Follow the workflow first; details follow.

## 🔁 Quick Workflow
1. Disable IBus emoji shortcut (optional): `ibus-setup` → Emoji → clear shortcut.
2. Adjust text scaling: Settings → Accessibility → Large Text (or install Tweaks for fine control).
3. Enable firewall: `sudo ufw enable` → check with `sudo ufw status`.
4. Attach Ubuntu Pro (free ≤5 machines) & enable Livepatch (if you have a token): `sudo pro attach <TOKEN>` → `sudo pro enable livepatch`. (https://ubuntu.com/pro/dashboard)
5. Install tools: `sudo apt install -y htop net-tools gnome-tweaks rkhunter chkrootkit`.
6. Run baseline checks: `htop`, `sudo netstat -tulnp`, `sudo rkhunter --check`, `sudo chkrootkit`.
7. Inspect startup + auth logs: `systemctl list-unit-files --state=enabled`, `grep "Failed password" /var/log/auth.log`.
8. Open project folder in VS Code: `code .`.

---

## 1. Input & Keyboard
### Disable IBus Emoji Annotation (Ctrl+.)
Prevents stray underlined "e" placeholder.
```bash
ibus-setup
```
Emoji tab → Emoji annotation shortcut → ... → Backspace → Apply (shows Disabled). Restart affected apps if needed.

## 2. System Settings & Fonts
### Open Settings / Specific Panel
```bash
gnome-control-center            # main settings
gnome-control-center display    # open Display panel directly
```
### Text Scaling
Coarse: Settings → Accessibility → Large Text.

Granular: install Tweaks then adjust scaling factor.
```bash
sudo apt install -y gnome-tweaks
```
Tweaks → Fonts → Scaling Factor (e.g. 1.15–1.25).

## 3. Development Convenience
### Open Current Directory in VS Code
```bash
code .
```
If `code` not found: VS Code → Command Palette → "Shell Command: Install 'code' command".

## 4. Security & Monitoring
### 4.1 Firewall (UFW)
```bash
sudo ufw enable
sudo ufw status verbose
```
### 4.2 Processes / Resources
```bash
sudo apt install -y htop
htop
```
Look for unknown high-usage processes.
### 4.3 Network Listeners / Ports
```bash
sudo apt install -y net-tools
sudo netstat -tulnp
```
### 4.4 Rootkit / Malware Scans
```bash
sudo apt install -y rkhunter chkrootkit
sudo rkhunter --update   # optional
sudo rkhunter --check
sudo chkrootkit
```
Review warnings (false positives possible).
### 4.5 Startup Services
```bash
systemctl list-unit-files --state=enabled
```
Investigate unfamiliar entries.
### 4.6 Authentication Failures
```bash
grep "Failed password" /var/log/auth.log | tail -n 20
```
Repeated attempts from same IP may signal brute force.

### 4.7 Ubuntu Pro (ESM + Livepatch)
Extends security coverage to Universe packages (ESM) and applies critical kernel patches without reboot (Livepatch). Free for personal use (up to 5 machines).

Benefits (condensed):
- ESM: Canonical patches thousands of Universe packages (extends supported lifetime to 10y).
- Livepatch: Kernel CVE fixes without reboot → less downtime, fewer delayed updates.

Commands:
```bash
pro status                      # or: sudo pro status (shows entitlements)
sudo pro attach <TOKEN>         # attach subscription (get token from ubuntu.com/pro)
sudo pro enable livepatch       # enable kernel livepatching
sudo pro refresh                # refresh contract data
sudo pro detach --assume-yes    # (optional) remove subscription
```
Verification:
```bash
pro status | grep -E 'esm|livepatch'
```
Livepatch active line should show: enabled / running.

## 5. Command Reference (Copy/Paste Block)
```bash
# IBus preference
ibus-setup

# Settings
gnome-control-center
gnome-control-center display

# Text scaling tweaks
sudo apt install -y gnome-tweaks

# VS Code current folder
code .

# Firewall
sudo ufw enable
sudo ufw status verbose

# Monitoring
sudo apt install -y htop net-tools
htop
sudo netstat -tulnp

# Rootkit scans
sudo apt install -y rkhunter chkrootkit
sudo rkhunter --check
sudo chkrootkit

# Startup + auth
systemctl list-unit-files --state=enabled
grep "Failed password" /var/log/auth.log

# Ubuntu Pro
pro status
sudo pro attach <TOKEN>
sudo pro enable livepatch
pro status | grep -E 'esm|livepatch'
```

---
Minimal core only; extend with package updates, backups, and user management as needed.