[README](#readme)
- [README](#readme)
  - [Install WSL](#install-wsl)
  - [Install, configure and update `git`](#install-configure-and-update-git)
  - [Install others (optional)](#install-others-optional)
    - [Install DVC](#install-dvc)
    - [Install lefthook](#install-lefthook)
    - [Install pip](#install-pip)
    - [Install `git-filter-repo`](#install-git-filter-repo)
  - [This repository contains submodules](#this-repository-contains-submodules)
  - [Export and Import](#export-and-import)
  - [`dive` into the image](#dive-into-the-image)
    - [Initialize/Update `okatsn/my-workspace`](#initializeupdate-okatsnmy-workspace)
  - [Trouble shooting](#trouble-shooting)
    - [Git](#git)
    - [Permission Denied on mounted volumes](#permission-denied-on-mounted-volumes)
    - [Docker](#docker)
    - [DVC](#dvc)
    - [Remove Zone.Identifier](#remove-zoneidentifier)
    - [Error "Are you trying to mount a directory onto a file (or vice-versa)?"](#error-are-you-trying-to-mount-a-directory-onto-a-file-or-vice-versa)
    - [Grant sudo for jovyan](#grant-sudo-for-jovyan)


# README

## Install WSL
Open the Windows Terminal, install WSL2 and the Ubuntu-24.04 distribution as default with the following command.

```bash
wsl --update
wsl --install -d Ubuntu-24.04
wsl --set-default Ubuntu-24.04
```

> 💡Useful tips:
> - If connection problem occurs (e.g., Failed to fetch ...; the connection to server was reset ...), run `wsl --shutdown` and try again.

Confirm the followings:
- `wsl -l -v`: Check if your Ubuntu-24.04 distribution uses WSL 2.
- `wsl --set-version Ubuntu-24.04 2`: Set WSL version to `2` if it is not.

## Install, configure and update `git`

VSCode extensions such as `mhutchie.git-graph` use `git`. 
Here is how to install `git`:
- `sudo apt-get update`
- `sudo apt-get install git`
> 💡 These are exactly the same commands to update Git in linux.

ONLY IF the it was not the latest `git` being installed, try either the followings: 
- `sudo apt-get dist-upgrade`
- `sudo add-apt-repository ppa:git-core/ppa`
> It's usually recommended to run `sudo apt-get update` before running `sudo apt-get dist-upgrade`.

Configuration:
- `git config --global user.name "YOUR_USERNAME"`
- `git config --global user.email "YOUR_ADDRESS@Xmail.com"`

## Install others (optional)

### Install DVC

Please refer to [DVC-Installation on Linux](https://dvc.org/doc/install/linux#installation-on-linux) or [this Dockerfile](https://github.com/okatsn/MyTeXLife/blob/main/.devcontainer/Dockerfile) to install DVC.


### Install lefthook
[Lefthook Documentaion](https://github.com/evilmartians/lefthook)

1. Install
```
sudo snap install --classic lefthook
```
2. Create `lefthook.yml`.
3. Stage files
4. Run 
   - It will run `pre-commit` before actually commit (`git commit -m "Commit message"`).
   - You can also run on demand: `lefthook run pre-commit`

!!! warning
    - **Commit with VSCode's button will not trigger the lefthook actions.**
    - Lefthook has to be installed in WSL (not in container) if the command have `docker`-whatever in use.


### Install pip

If you want to use `pip`, consider using `pipx` instead:

```
sudo apt install pipx
```

The reason is that, install python3 (e.g., `sudo apt install python3-full`) in WSL do not immediately allow `pip` ready to use; typically you will get an error message "This environment is externally managed".


### Install `git-filter-repo`

```
sudo apt install git-filter-repo
```

You can use this package to remove files totally from the history.

For example: 

```
git-filter-repo --invert-paths --path path/to/file/or/directory
```

After remove files from all the commits, you might need to add remote back again, for example:


Make sure your remote is missing
```
git remote -v
```

Add the remote back 
```
git remote add origin https://github.com/okatsn/HelloWorld.git
```

Set the local `main` as upstream again; Noted that the remote `main` will be overwritten in this step.
```
git push --force --set-upstream origin main
```

Overwrite all other branches on the remote
```
git push origin --all --force
```

Remove Old Remote References
```
git fetch origin --prune
```

Remove Dangling References
```
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

Make sure the files are completely removed

```
git clone <repository-url>
cd <repository-name>
git log --all -- path/to/file
```

Some instructions of this section is ChatGPT's advices. 
Please refer [git-filter-repo(1) Manual Page](https://htmlpreview.github.io/?https://github.com/newren/git-filter-repo/blob/docs/html/git-filter-repo.html), [newren/git-filter-repo](https://github.com/newren/git-filter-repo) and [How to remove file from Git history?](https://stackoverflow.com/questions/43762338/how-to-remove-file-from-git-history)

## This repository contains submodules

## Export and Import
Referring [How can I change the location of docker images when using Docker Desktop on WSL2 with Windows 10 Home?](https://stackoverflow.com/questions/62441307/how-can-i-change-the-location-of-docker-images-when-using-docker-desktop-on-wsl2)
> A similar ref.: https://needlify.com/post/how-to-move-wsl-distributions-including-docker-images-to-new-locations-on-windows-6412384cbd14c

In windows Terminal, 
list all the distributions:
```
wsl --list -v
```

```
  NAME                   STATE           VERSION
* Ubuntu-24.04           Running         2
  Ubuntu-22.04           Stopped         2
  docker-desktop-data    Stopped         2
  Ubuntu-20.04           Stopped         2
  docker-desktop         Stopped         2
```
> Use `wsl --shutdown` in case the one you are going to move is running. See also [Move docker-desktop-data distro out of System Drive](https://dev.to/kim-ch/move-docker-desktop-data-distro-out-of-system-drive-4cg2)

**Export**
```
wsl --export docker-desktop-data "D:\temp\docker-desktop-data.tar"
```

**Unregister** old
```
wsl --unregister docker-desktop-data
```

**Import** to the target (e.g., "D:\WSL\data")
```
wsl --import docker-desktop-data "D:\WSL\data" "D:\temp\docker-desktop-data.tar" --version 2
```
## `dive` into the image

[Install dive](https://github.com/wagoodman/dive?tab=readme-ov-file#installation) on WSL.

Using `dive` to inspect what modifications were made in one layer:

Example
```bash
cd ./python-debian-build
docker-compose --env-file ../my-build.env build --no-cache
dive pbuild
```

Example (list the already built images, and choose one to dive into)

```bash
docker image list
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

#### build

Build container in VSCode based on `devcontainer.json` may fail with a short and ambiguous message on different user settings.
Here is an [Example](https://github.com/microsoft/vscode-remote-release/issues/9461). 
Switch the settings to your recent profile on another PC may solve the problem.

#### Clean volumes, containers and images

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

#### Use a local build for quick testing
(following `julia-debian-build/README.md`)
- Create a temporary local build: `docker tag jbuild temp-local:latest`, and
- use it in other Dockerfile `FROM temp-local AS build-julia`.


### DVC

Every time a container is rebuilt, you'll experience the auth process again.
If you encounter authorization issues when trying to grant DVC permissions to access Google drive, manually copy existing credentials to the new virtual machine could bypass the process and might solve the problem.

Please refer https://dvc.org/doc/user-guide/data-management/remote-storage/google-drive#authorization

Here are an example workflow: 
- Save `default.json` file in the machine where DVC can access your Google Drive. This file locates at `~/.cache/pydrive2fs/xxxxxxxx-xxxxxxxxxxxxxxx.apps.googleusercontent.com/default.json`.
- In the new machine, `dvc status -c` to print messages as follows and confirm that it prints identical  `xxxxxxxx-xxxxxxxxxxxxxxx` part.
  ```
  0% Checking cache in '1XXXXXXXXXXXXX-xx/files/md5'|                                                        |0/? [00:00<?,    ?files/s]oauth2client/_helpers.py:255: UserWarning: Cannot access /home/jovyan/.cache/pydrive2fs/xxxxxxxx-xxxxxxxxxxxxxxx.apps.googleusercontent.com/default.json: No such file or directory
  ```
- Copy `default.json` to the new machine at the same place, and DVC should access Google Drive as the old machine.


### Remove Zone.Identifier

```
find ./ -type f -name "*:Zone.Identifier" -exec rm -f {} \;
```

- `type f`: This restricts the search to files (excluding directories).
- `exec rm -f {} \;`: This runs the `rm` command on each file found. The `{}` is replaced with the filename, and `\;` indicates the end of the command.

### Error "Are you trying to mount a directory onto a file (or vice-versa)?"

When you reset your WSL distro, you might encounter this kind of non-sense error.
[Clean volumes, containers and images](#clean-volumes-containers-and-images) and restart docker desktop might solve the problem.

See [this post](https://stackoverflow.com/questions/45972812/are-you-trying-to-mount-a-directory-onto-a-file-or-vice-versa).


### Grant sudo for jovyan

To use sudo, not only `GRANT_SUDO` has to be "yes", but also user to be root. See 
- https://github.com/jupyter/docker-stacks/issues/949
- https://stackoverflow.com/questions/78460730/what-is-the-password-for-jovyan-user-in-jupyter-lab-docker-container and links therein: https://github.com/jupyter/docker-stacks/issues/408#issuecomment-1588023099

You can set user in `docker-composer.yml` at:

```
services:
  yourcontainername: 
    user: root
    environment:
      GRANT_SUDO: "yes"
```

or in `devcontainer.json`, set `"remoteUser": "root",`, such that when you open an integrated terminal in VS Code within the Dev Container you'll be logged in as the root user.
However, the problem is if the the terminal user is root, many things go wrong due to permission mismatch, including that GIT will be unavailable when the folder is opened in this DevContainer (GIT authentication is granted in WSL for user `okatsn`, and in DevContainer `jovyan` should have the same UID as `okatsn` for user to work smoothly in the containerized workspace).