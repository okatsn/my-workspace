# Use Go builder for getting Go installation
FROM okatsn/my-go-build:v2024 AS go-build

# Use minimal base image
FROM ubuntu:latest

# Set noninteractive installation
ENV DEBIAN_FRONTEND=noninteractive

# KEYNOTE:
# This Dockerfile aims for building a containerized utility box for arbitrary users. See README for more details.
# How the Dockerfile is structured to handle permissions for arbitrary users:
# 1. Install tools as root and place them in global paths like bin
# 2. Create the appuser after installing the tools
# 3. Set appuser as the default container user for security

# Install basic utilities
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    jq \
    unzip \
    ruby \
    # Clean
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy Go from builder and set up Go environment
COPY --from=go-build /usr/local/go /usr/local/go
ENV PATH=/usr/local/go/bin:${PATH}

# Install tools globally (as root)
RUN gem install mustache && \
    go install go.abhg.dev/stitchmd@latest && \
    cp $(go env GOPATH)/bin/stitchmd /usr/local/bin/

# Install stitchmd:
# A tool that stitches together several Markdown files into one large Markdown file, making it easier to maintain larger Markdown files.
# See: https://github.com/abhinav/stitchmd?tab=readme-ov-file#installation
# RUN go install go.abhg.dev/stitchmd@latest

# Create non-root user
RUN groupadd -g 1002 appuser && \
    useradd -u 1002 -g 1002 -m appuser





# # For document processing
# If fonts in PDF is missing, converting the output PDF to WORD might result in inconsistent font.
RUN apt-get update && apt-get -y install \
    fontconfig \
    fonts-noto-cjk \
    fonts-noto-cjk-extra \
    fonts-noto-color-emoji \
    # 中文類楷體
    fonts-arphic-ukai \
    # PDF utilities
    qpdf \
    ghostscript \
    pdftk-java \
    # Clean
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


## Install fonts that supports smcp
RUN wget https://github.com/adobe-fonts/source-serif/archive/refs/heads/release.zip -O /tmp/temp123.zip  \
    && unzip /tmp/temp123.zip -d /tmp/temp123  \
    && mkdir -p /usr/share/fonts/opentype/source-serif-pro \
    && cp /tmp/temp123/source-serif-release/OTF/*.otf /usr/share/fonts/opentype/source-serif-pro/ \
    && fc-cache -fv \
    && rm -rv /tmp/temp123 \
    && rm -rv /tmp/temp123.zip




# Switch to appuser for default operation
USER appuser
ENV GOPATH=/home/appuser/go
ENV PATH=${GOPATH}/bin:${PATH}

# Set working directory
WORKDIR /workspace

# # Use ENTRYPOINT to make the container behave like a CLI tool
# Set this if you want a interface such as docker run okatsn/my-util-box "ls -la" rather than docker run okatsn/my-util-box ls -la
ENTRYPOINT ["sh", "-c"]


# Default command (can be overridden)
CMD ["echo 'Available commands: jq, stitchmd, go, unzip, mustache'"]