# typst-mirror

`okatsn/my-typst-space` is a copy of the official image `ghcr.io/typst/typst:<TYPST_VERSION>` (published by [typst/typst](https://github.com/typst/typst) on every release); nothing is built here.

`TYPST_VERSION`, `TYPST_RELEASE` and `TYPST_REV` are set in [release.env](../release.env) (see [Version bump](../my-jupyter-with-julia/README.md#version-bump-julia--quarto--typst)).

```bash
# In the typst-mirror directory: smoke test the official image and copy it (registry-side) to
# `v<major>.<minor>-<RELEASE>.<REV>`, `v<major>.<minor>-<RELEASE>` and `latest`
./docker_build_and_push.sh
```

It fails, pushing nothing, if the upstream tag does not exist, `typst --version` is not `TYPST_VERSION`, or the immutable tag already exists (bump `TYPST_REV`).

## Use the image

In Dockerfile (the tag is an immutable one derived from `release.env`):

```Dockerfile
FROM okatsn/my-typst-space:v0.14-2026a.0 AS build0
COPY --from=build0 /bin/typst /bin
```

The previous tags (e.g., `v2026a`) were built from the former submodule `typst-official-build` (okatsn/my-typst-space) and remain in the registry.
