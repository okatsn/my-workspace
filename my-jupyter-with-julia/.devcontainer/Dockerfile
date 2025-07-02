FROM okatsn/my-jupyter-with-julia:v2025d.1

USER root

# # Utilities for individual containers. Feel free to customize the list below.
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
    ghostscript && \ 
    fc-cache -f -v 

USER $NB_USER
