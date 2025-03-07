# Use Go builder for getting Go installation
FROM okatsn/my-go-build:v2024 AS go-build

# Use minimal base image
FROM ubuntu:latest

# Set noninteractive installation
ENV DEBIAN_FRONTEND=noninteractive

# Install basic utilities
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    jq \
    unzip \
    ruby \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -g 1002 appuser && \
    useradd -u 1002 -g 1002 -m appuser

# Copy Go from builder and set up Go environment
COPY --from=go-build /usr/local/go /usr/local/go
ENV GOPATH=/home/appuser/go
ENV PATH=/usr/local/go/bin:${GOPATH}/bin:${PATH}

# Switch to appuser for installing user-specific packages
USER appuser

# Install mustache (ruby gem)
RUN gem install --user-install mustache

# Install stitchmd
RUN go install go.abhg.dev/stitchmd@latest

# Set working directory
WORKDIR /workspace

# # Use ENTRYPOINT to make the container behave like a CLI tool
# Set this if you want a interface such as docker run okatsn/my-util-box "ls -la" rather than docker run okatsn/my-util-box ls -la
ENTRYPOINT ["sh", "-c"]


# Default command (can be overridden)
CMD ["echo 'Available commands: jq, stitchmd, go, unzip, mustache'"]