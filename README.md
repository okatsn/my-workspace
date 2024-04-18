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

## This repository contains submodules

### Initialize/Update `okatsn/my-workspace`

!!! warn This script is given by ChatGPT and have not been tested!
Initialize
```bash
git clone --recursive https://github.com/okatsn/my-workspace.git
# or if the repo was already cloned without --recursive
cd my-workspace
git submodule init
git submodule update

```

CHECKPOINT: https://chat.openai.com/c/30c3b844-d39a-4ab2-b6c9-3c92b24484ff

Update
```bash
cd sub-something
git checkout master # or main, depending on the branch
git pull origin master # or the branch you are tracking
cd ..
git add sub-something
git commit -m "Update submodule to latest original source"

```
### Add and remove submodules
```bash
# Add a submodule of name sub-something
git submodule add https://github.com/okatsn/MyTeXLife.git my-tex-life
git commit -m "Add MyTeXLife as submodule"

```