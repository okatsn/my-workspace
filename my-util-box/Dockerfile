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

# Install mustache (ruby gem)
RUN gem install mustache

# Copy Go from builder and set up Go environment
COPY --from=go-build /usr/local/go /usr/local/go
ENV GOPATH=/root/go
ENV PATH=/usr/local/go/bin:${GOPATH}/bin:${PATH}

# Install stitchmd
RUN go install go.abhg.dev/stitchmd@latest

# Set working directory
WORKDIR /workspace

# Use ENTRYPOINT to make the container behave like a CLI tool
ENTRYPOINT ["sh", "-c"]
# Default command (can be overridden)
CMD ["echo 'Available commands: jq, stitchmd, go, unzip, mustache'"]