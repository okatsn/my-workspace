FROM debian:bullseye-slim

# Install necessary tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    tar \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Download and install Go
ENV GO_VERSION=1.21.0
RUN wget "https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz" \
    && tar -C /usr/local -xzf "go${GO_VERSION}.linux-amd64.tar.gz" \
    && rm "go${GO_VERSION}.linux-amd64.tar.gz"

# Set Go environment variables
ENV GOPATH=/go
ENV PATH=/usr/local/go/bin:${GOPATH}/bin:${PATH}

# Verify Go installation (optional)
RUN go version