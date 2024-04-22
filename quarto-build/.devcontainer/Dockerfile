# Build stage
FROM okatsn/my-typst-space AS build0

FROM okatsn/my-julia-space:v1.9.4

USER $NB_USER
WORKDIR $WORKSPACE_DIR

ARG VSCODE_PATH="Foo"
ARG VSCODE_INSIDER_PATH="Bar"
# # Set enviroment variable
ENV VSCODE_PATH=${VSCODE_PATH} \
    VSCODE_INSIDER_PATH=${VSCODE_INSIDER_PATH}

RUN mkdir -p $VSCODE_PATH/extensions \
    $VSCODE_INSIDER_PATH/extensions \
    $SUB_PROJECT_DIR \
    && chown -R $NB_USER \
    $VSCODE_PATH \
    $VSCODE_INSIDER_PATH


COPY .devcontainer/startup_ijulia.jl /home/$NB_USER/.julia/config/startup_ijulia.jl

# ENTRYPOINT ["julia", "--project=@.", "-e", "'using Pkg; Pkg.build(\"IJulia\")'"]
# ENTRYPOINT ["julia", "--project=@.", "-e", "'using Pkg; println(pwd()); show(Pkg.status())'"]

# Copy the built binary from the Rust build stage to the final stage
COPY --from=build0 /bin/typst /bin
# Please refer https://github.com/okatsn/my-typst-space