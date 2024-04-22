# About Docker

## Useful resources
- [Debugging Docker builds](https://www.joyfulbikeshedding.com/blog/2019-08-27-debugging-docker-builds.html) (from thread [How to debug build failures](https://forums.docker.com/t/how-to-debug-build-failures/7049/3))

## CHECKPOINT
- `RUN conda env update --file environment.yml` failed due to `UnsatisfiableError: The following specifications were found to be incompatible with a past`. This error occurrs even after I pin the minimal-notebook to `FROM jupyter/minimal-notebook@sha256:b4f6e2ccd7af513254388fd11012c849e8e9461f643c34ddcf446dd99bd689a6`, with all versions assigned in environment.yml the same as the previously successfully built container.
- `RUN conda env create -f environment.yml` failed: `CondaValueError: prefix already exists: /opt/conda`