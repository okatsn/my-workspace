FROM okatsn/my-julia-build:v1.10-2024a as build-julia

# Please refer to https://jupyter-docker-stacks.readthedocs.io/en/latest/using/selecting.html#jupyter-minimal-notebook
# # Docker image repository seems to moved to quay.io
# # The list of available tags: https://quay.io/repository/jupyter/minimal-notebook?tab=tags
FROM quay.io/jupyter/minimal-notebook:2024-07-15

# Referring https://jupyter-docker-stacks.readthedocs.io/en/latest/using/common.html#user-related-configurations
ENV CHOWN=yes


USER root


COPY --from=build-julia --chown=$NB_UID:$NB_GID /home/okatsn/.julia /home/$NB_USER/.julia

COPY --from=build-julia --chown=$NB_UID:$NB_GID /opt/julia-okatsn /opt/julia-okatsn

# Create link in the new machine (based on that /usr/local/bin/ is already in PATH)
RUN ln -fs /opt/julia-okatsn/bin/julia /usr/local/bin/julia


# Switch to $NB_USER
# # Switch to $NB_USER is essential for the following RUN julia -e ...
# # because associated files and directories are owned by NB_USER
USER $NB_USER


# Build IJulia
RUN julia -e 'using Pkg; Pkg.update(); Pkg.instantiate(); Pkg.build("IJulia");' 

