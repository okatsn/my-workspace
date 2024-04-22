
### Push and use Docker image

[Ref.](https://docs.docker.com/engine/reference/commandline/commit/)

Once an image is successfully built, commit and push the image as follows:

#### Get container ID
**in wsl**
- `docker container list` to get the CONTAINER_ID 

**in Docker Desktop**
- click on tab "Containers" 
- expand the droplist of `myjuliaspace_devcontainer` and it shows

#### Commit

- In wsl, `docker commit CONTAINER_ID user/repo` 
    - e.g., `docker commit 3935a2cd9ee6 okatsn/my-julia-space`

commit with a tag and message:
- `docker commit -m "Hello World!" 89065a96c90b okatsn/my-tex-life-with-julia:helloworld`

#### Push committed image (with tag)

Push committed image
- in wsl, `docker image push okatsn/my-julia-space`
- By default it pushes the image with the tag of `latest`.

Push the image with the `helloworld` tag:
- `docker image push okatsn/my-julia-space:helloworld`

#### To use the image:
- in .devcontainer/Dockerfile, with `FROM okatsn/my-julia-space`
- add .devcontainer/docker-compose.yml
- add .devcontainer/devcontainer.json