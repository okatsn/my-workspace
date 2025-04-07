# README

## How to use

In Dockerfile:

```Dockerfile
FROM okatsn/my-go-build:latest AS my-go-build
```


```Dockerfile
# Under root user

# Copy Go installation from the builder stage - still as root
COPY --from=my-go-build /usr/local/go /usr/local/go
# Set Go environment variables (although there is no "/go" in the container, this ENV should be defined to tell that it is the workspace for go.)
ENV GOPATH=${HOME}/go  
# Set GOPATH within user's home
ENV PATH=/usr/local/go/bin:${GOPATH}/bin:${PATH}
```

then you can use `GO`, for example, to install something like:

```Dockerfile
# Install stitchmd:
# A tool that stitches together several Markdown files into one large Markdown file, making it easier to maintain larger Markdown files.
# See: https://github.com/abhinav/stitchmd?tab=readme-ov-file#installation
RUN go install go.abhg.dev/stitchmd@latest

```