# CHECKPOINT: When I'm trying to build a new container base on it (saying `FROM okatsn/my-latex-devcontainer`), permission error occurred when the docker-compose.yml of the new container also create/attach the volume of .vscode-server.
# The error is fixed when I build the image again using the following command instead; previously, the image was build using docker-compose.yml.
# However, I cannot reproduce the error again. I'm not sure the permission denied error is solved by using the following building command, or by remove all the my-latex-devcontainer--related containers, images and volumes.
#
# Building command:
# # `devjuliatex` and `my-latex-devcontainer` can be replaced by arbitrary names.
# # Remember to change the tag name before build and push.
# $ docker build -t devjuliatex -f .devcontainer/Dockerfile .
# $ docker tag devjuliatex okatsn/my-latex-devcontainer:latest
# $ docker push okatsn/my-latex-devcontainer:latest


FROM okatsn/my-typst-space:v2026a AS build0

FROM okatsn/my-tex-life:v2026a
# Docker image https://hub.docker.com/repository/docker/okatsn/my-tex-life/general built from https://github.com/okatsn/MyTeXLife


USER root

# Under root user



# # Install Zotero
RUN curl -sL https://raw.githubusercontent.com/retorquere/zotero-deb/master/install.sh | bash
RUN apt-get update && apt-get -y install \
    zip \
    tree \
    zotero
# Get the better-bibtex file
COPY .devcontainer/get_zoteroaddons.sh /tmp/
RUN chmod +x /tmp/get_zoteroaddons.sh && \
    . /tmp/get_zoteroaddons.sh
# TODO: Install Zotero and BibTeX (cannot be done in Dockerfile)
# KEYNOTE: . /tmp/get_zoteroaddons.sh is prefered than sh /tmp/get_zoteroaddons.sh, where in the later sh might not be available. See https://stackoverflow.com/a/34217720
# - Download Better BibTeX: https://github.com/retorquere/zotero-better-bibtex/releases/latest
# - $ zotero          // open zotero (a window of zotero app should pop out)
# - In Zotero app, click Tools > Add-ons > ⚙️ (setting icon) > Install Add-on from file... and click on the zotero-better-bibtex-6.7.143.xpi you just downloaded.
#
# KEYNOTE: How to use
# - Open Zotero ($ zotero)
# - Use VSCode addon XING.zotero-cite "Zotero Cite: Cite and Create Bibliograph for Pandoc/LaTeX." (it creates bibtex.bib for main.tex for example), or use raykr.zotex "Zotex: Cite and Create Bibliograph for LaTeX."



# CHECKPOINT: Multi stage build; Merge these keynotes to the README of my-latex-devcontainer
# https://cindyliu923.com/2021/05/23/What-is-docker-multi-stage/
# - Explanation: What are inside an image?  layers!
# - Keypoints: Middle images won't presents as layers in the final image.
# - All files and folders not `COPY`ed won't survive in the final stage. (?!)
# - Application: Thus you can have some secrets inside the middle image!

# https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#use-multi-stage-builds
# - Only the instructions RUN, COPY, ADD create layers.


# # For Typst
# # # Install Rust
# # # Please refers https://www.rust-lang.org/learn/get-started. `-s -- -y` is suggested by ChatGPT in order to install using default settings without interrupt.
# RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y






# Install DVC
RUN wget https://dvc.org/deb/dvc.list -O /etc/apt/sources.list.d/dvc.list \
    && wget -qO - https://dvc.org/deb/iterative.asc | gpg --dearmor > packages.iterative.gpg \
    && install -o root -g root -m 644 packages.iterative.gpg /etc/apt/trusted.gpg.d/ \
    && rm -f packages.iterative.gpg \
    && apt update \
    && apt -y install dvc=3.53.2 \
    && dvc completion -s bash | tee /etc/bash_completion.d/dvc


#  Cleans up the package list cache, which is no longer needed after installation and helps reduce the final image size.
RUN rm -rf /var/lib/apt/lists/*



# This allow starship to create log. See comments in my-jupyter-with-julia/Dockerfile
RUN mkdir -p /home/$NB_USER/.cache/starship && chown -R $NB_USER:$NB_GID /home/$NB_USER/.cache/starship


# WORKDIR $WORKSPACE_DIR
USER $NB_USER

COPY --from=build0 /bin/typst /bin
# Please refer: https://github.com/my-typst-space

