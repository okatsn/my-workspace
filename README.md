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

## Install and configure `git`

VSCode extensions such as `mhutchie.git-graph` use `git`. 
Here is how to install `git`:
- `sudo apt-get update`
- `sudo apt-get install git`

ONLY IF the it was not the latest `git` being installed, try either the followings: 
- `sudo apt-get dist-upgrade`
- `sudo add-apt-repository ppa:git-core/ppa`
> It's usually recommended to run `sudo apt-get update` before running `sudo apt-get dist-upgrade`.

Configuration:
- `git config --global user.name "YOUR_USERNAME"`
- `git config --global user.email "YOUR_ADDRESS@Xmail.com"`