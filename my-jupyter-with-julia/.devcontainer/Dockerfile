FROM okatsn/my-jupyter-with-julia:v2025f

USER root

RUN apt-get update && \
    apt-get -y install \
    fontconfig \
    # Install Tinos (the best Times New Roman alternative)
    fonts-croscore \
    # 中文類楷體
    fonts-arphic-ukai \
    # Google Notos
    fonts-noto-cjk \
    fonts-noto-cjk-extra \
    fonts-noto-color-emoji \
    # PDF utilities
    ghostscript \
    # # git-crypt
    # git-crypt \
    # gnupg \
    # Final clean
    && fc-cache -f -v


## Install fonts that supports smcp
RUN wget https://github.com/adobe-fonts/source-serif/archive/refs/heads/release.zip -O /tmp/temp123.zip  \
    && unzip /tmp/temp123.zip -d /tmp/temp123  \
    && mkdir -p /usr/share/fonts/opentype/source-serif-pro \
    && cp /tmp/temp123/source-serif-release/OTF/*.otf /usr/share/fonts/opentype/source-serif-pro/ \
    && fc-cache -fv \
    && rm -rv /tmp/temp123 \
    && rm -rv /tmp/temp123.zip

# RUN apt update && apt install -y \
# # For `npx degit`; it costs around 366 MB.
# npm \
# # Install imagemagick that allows png-jpg conversion
# # - Rotate image in-place: `mogrify -rotate 90 sancen-1-photo-4.png`
# imagemagick

USER $NB_USER
