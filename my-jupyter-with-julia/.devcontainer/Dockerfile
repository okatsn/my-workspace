FROM okatsn/my-jupyter-with-julia:v2026c

USER root

RUN apt-get update && \
    apt-get -y install \
    fontconfig \
    # # DejaVu Sans & DejaVu Sans Mono (required by Documenter's documenter.sty)
    fonts-dejavu \
    # # Install Tinos (the best Times New Roman alternative)
    # fonts-croscore \
    # # 中文類楷體
    # fonts-arphic-ukai \
    # # Google Notos
    # fonts-noto-cjk \
    # fonts-noto-cjk-extra \
    # fonts-noto-color-emoji \
    # Copilot sandboxing
    bubblewrap \
    socat \
    # PDF utilities
    ghostscript \
    # # git-crypt
    # git-crypt \
    # gnupg \
    # Final clean
    ## For Claude `docx` skill (okatsn/claude-skills)
    # libreoffice \
    # poppler-utils \
    ## Final clean
    && fc-cache -f -v

# ## For Claude `docx` skill: install docx JS library for creating new Word documents
# RUN apt update && apt install -y \
#     ## Why npm is required:
#     # 1. For `npx degit`; it costs around 366 MB.
#     # 2. npm is required for `npm install -g docx` (docx skill: creating new Word documents)
#     npm \
#     # Install imagemagick that allows png-jpg conversion
#     # - Rotate image in-place: `mogrify -rotate 90 sancen-1-photo-4.png`
#     imagemagick

# # Make globally installed npm packages resolvable via require()
# ENV NODE_PATH=/usr/local/lib/node_modules
# # For docx skill
# RUN npm install -g docx


# ## Install fonts that supports smcp
# RUN wget https://github.com/adobe-fonts/source-serif/archive/refs/heads/release.zip -O /tmp/temp123.zip  \
#     && unzip /tmp/temp123.zip -d /tmp/temp123  \
#     && mkdir -p /usr/share/fonts/opentype/source-serif-pro \
#     && cp /tmp/temp123/source-serif-release/OTF/*.otf /usr/share/fonts/opentype/source-serif-pro/ \
#     && fc-cache -fv \
#     && rm -rv /tmp/temp123 \
#     && rm -rv /tmp/temp123.zip


# ## Install tectonic LaTeX engine (prebuilt static binary, v0.15.0)
# # See https://github.com/tectonic-typesetting/tectonic/releases for latest version.
# # Install tectonic if you need to compile docs to PDF using Documenter.jl (requires LaTeX utilities).
# ARG TECTONIC_VERSION=0.15.0
# RUN wget -q \
#     "https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%40${TECTONIC_VERSION}/tectonic-${TECTONIC_VERSION}-x86_64-unknown-linux-musl.tar.gz" \
#     -O /tmp/tectonic.tar.gz \
#     && tar -xzf /tmp/tectonic.tar.gz -C /usr/local/bin \
#     && chmod +x /usr/local/bin/tectonic \
#     && rm /tmp/tectonic.tar.gz

USER $NB_USER

# Force Julia's Pkg to use the git CLI instead of LibGit2.
# This streamlines the process of adding package which is private but registered on public registry.
ENV JULIA_PKG_USE_CLI_GIT=true