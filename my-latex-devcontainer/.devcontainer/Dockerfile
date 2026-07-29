FROM okatsn/my-latex-devcontainer:v2026a
USER root

RUN apt-get update && \
    apt-get -y install \
    fontconfig \
    # # DejaVu Sans & DejaVu Sans Mono (required by Documenter's documenter.sty)
    # fonts-dejavu \
    # # Install Tinos (the best Times New Roman alternative)
    # fonts-croscore \
    # # 中文類楷體
    # fonts-arphic-ukai \
    # # Google Notos
    # fonts-noto-cjk \
    # fonts-noto-cjk-extra \
    # fonts-noto-color-emoji \
    # # Copilot sandboxing
    bubblewrap \
    socat \
    # # PDF utilities
    ghostscript \
    # # git-crypt
    # git-crypt \
    # gnupg \
    # # For Claude `docx` skill (okatsn/claude-skills)
    # libreoffice \
    # poppler-utils \
    # # Final clean
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && fc-cache -f -v

# # For pdf to docx converting skills
RUN pip install pdf2docx


# # For Mustache templating and Claude `docx` skill (with `curl` and `ca-certificates` already available)
# NOTE: Install nodejs with nodesource setup script in the previous [OJS] block automatically has npm installed.
# Why npm is required:
# 1. For `npx degit`; it costs around 366 MB.
# 2. npm is required for `npm install -g docx` (docx skill: creating new Word documents)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y \
    gnupg \
    nodejs \
    # Install imagemagick that allows png-jpg conversion
    # - Rotate image in-place: `mogrify -rotate 90 sancen-1-photo-4.png`
    imagemagick \
    ## Final clean
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# # Verify Node.js and NPM installation
RUN node -v && npm -v


# Make globally installed npm packages resolvable via require()
ENV NODE_PATH=/usr/local/lib/node_modules
# For docx skill
RUN npm install -g docx

# # # LATER: https://share.gemini.google/6ict9qKYq2Ro
# # For converting diff file to html
# # Example: `npx diff2html-cli -i file -s side -o stdout -- manuscript_0.diff > manuscript_0.html`
# RUN npm install -g diff2html-cli


# ## Install fonts that supports smcp
# RUN wget https://github.com/adobe-fonts/source-serif/archive/refs/heads/release.zip -O /tmp/temp123.zip  \
#     && unzip /tmp/temp123.zip -d /tmp/temp123  \
#     && mkdir -p /usr/share/fonts/opentype/source-serif-pro \
#     && cp /tmp/temp123/source-serif-release/OTF/*.otf /usr/share/fonts/opentype/source-serif-pro/ \
#     && fc-cache -fv \
#     && rm -rv /tmp/temp123 \
#     && rm -rv /tmp/temp123.zip


# # Install JQ
# RUN sudo apt update && sudo apt install -y jq

USER $NB_USER