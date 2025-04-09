FROM okatsn/my-jupyter-with-julia:latest

USER $NB_USER

# # Fix permissions for directories that is going to be mounted as volume but not-yet created when building this image. For those mounted as volume but user might need their permissions, directories must be made first.
#
# - The starship cache: allow starship to create log. 
RUN mkdir -p /home/$NB_USER/.cache/starship 
# && chown -R $NB_USER:$NB_GID /home/$NB_USER/.cache/starship

# pydrive2fs: persistent dvc remote credentials.
RUN mkdir -p /home/$NB_USER/.cache/pydrive2fs
# && chown -R $NB_USER:$NB_GID /home/$NB_USER/.cache/pydrive2fs