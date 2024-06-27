# README

## Install WSL
Open the Windows Terminal, install WSL2 and the Ubuntu-24.04 distribution as default with the following command.

```bash
wsl --install -d Ubuntu-24.04
wsl --set-default Ubuntu-24.04
```

Confirm the followings:
- `wsl -l -v`: Check if your Ubuntu-24.04 distribution uses WSL 2.
- `wsl --set-version Ubuntu-24.04 2`: Set WSL version to `2` if it is not.

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

## `dive` into the image
Using `dive` to inspect what modifications were made in one layer:

Example
```bash
cd ./python-debian-build
docker-compose --env-file ../my-build.env build --no-cache
dive pbuild
```


Referring https://github.com/wagoodman/dive
### Initialize/Update `okatsn/my-workspace`


Initialize
```bash
git clone --recurse-submodules https://github.com/okatsn/my-workspace.git
# The `--recurse-submodules` is available for Git 2.13 or later, which is more efficient than `--recursive`. See https://stackoverflow.com/questions/3796927/how-do-i-git-clone-a-repo-including-its-submodules
cd my-workspace
git submodule init
git submodule update
```


## Trouble shooting
### Git

If you encounter authentication issues, an easy way to authenticate is use `gh` to open a page in your Windows browser and authenticate this WSL machine:

```bash
sudo apt update
sudo apt install gh
```

```bash
gh auth login
```

See also:
- [Installing gh on Linux and BSD](https://github.com/cli/cli/blob/trunk/docs/install_linux.md)
- [About authentication to GitHub](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-authentication-to-github)
- [gh auth login](https://cli.github.com/manual/gh_auth_login)

### Permission Denied on mounted volumes

For example, if you mount the `~/.ssh` in host to `/home/jovyan/.ssh` in container, "Permission denied" error will occur IF **the default user of host** (e.g., `okatsn`) do not have permissions. Many of these issues can be solved by executing the following code on **host**:

```bash
sudo chown -R okatsn:okatsn /home/okatsn/
```

Hints for trouble shooting this kind of issues:
- Check user id and group id of the default user in **host** and  **container** separately. (Use `id -g [<username>]` and `id [<username>]`)
- Use `ls -la` to check the folder/file that causes a Permissions-denied error in **host** and  **container** separately.
- Use `sudo chown [-R]` as needed.
- Use `chmod 755 <filename>` to fix the modifiability of a certain file as needed. `755` (drwxr-xr-x) is a typical permission for those in the home directory that should be.
> (`[]` denotes optional arguments or flags)


### Docker

Use the following command if it fails to build in one machine but success in the other with exactly the same script.
- `docker image prune`:  Clear images
- `docker builder prune`:  Clear Build Cache
- `docker volume prune`: Remove Unused Volumes
- `docker system prune -a --volumes`: Remove systemwide volumes. (DANGER!)
- `docker container prune`: Remove all stopped container.

See references:
- [docker system](https://docs.docker.com/reference/cli/docker/system/)
- [Remove All Containers and Images in Docker](https://www.geeksforgeeks.org/remove-all-containers-and-images-in-docker/)
- [Problem building dockerfile-with-features after upgrading to debian bookworm](https://github.com/microsoft/vscode-remote-release/issues/8202)