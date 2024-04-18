# README

## Install WSL
Open the Windows Terminal, install WSL2 and the Ubuntu-22.04 distribution as default with the following command.

```bash
wsl --install -d Ubuntu-22.04
wsl --set-default Ubuntu-22.04
```

Confirm the followings:
- `wsl -l -v`: Check if your Ubuntu-22.04 distribution uses WSL 2.
- `wsl --set-version Ubuntu-22.04 2`: Set WSL version to `2` if it is not.