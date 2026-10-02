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

## Why a mirror (design note)

Only `/bin/typst` is used downstream (`COPY --from=build0 /bin/typst /bin`), so the mirror is **not technically required**: `FROM ghcr.io/typst/typst:<TYPST_VERSION>` would give the same binary. It is kept deliberately:
- **Consistency:** like Julia and Quarto, Typst is an image of `okatsn/*` with an immutable `v<major>.<minor>-<RELEASE>.<REV>` tag derived from `release.env`, so `my-jupyter-with-julia` consumes all three build images the same way (`*_BUILD_REF`).
- **Fewer upstream registries at build time:** later rebuilds of `my-jupyter-with-julia` do not depend on ghcr.io being up, nor on upstream keeping a tag unchanged (the official semver tags are not guaranteed immutable).

The cost is one more manual step per Typst bump (run this script before building the jupyter image).

### If you decide to drop the mirror

1. In [release_vars.sh](../shscripts/release_vars.sh), set `TYPST_BUILD_REF` to `$TYPST_UPSTREAM_REF` (optionally pinned by digest, i.e., `...:<VERSION>@sha256:...`), then remove `TYPST_BUILD_IMAGE`, `TYPST_BUILD_TAG`, `TYPST_BUILD_CHANNEL`, `TYPST_RELEASE` and `TYPST_REV` (and `release.env`/`check_format` lines for them); keep `TYPST_VERSION`.
2. Delete this folder, and the whole `if [ -n "${MIRROR_FROM:-}" ]; then ... fi` block, the `MIRROR_FROM` lines in the header comment, and the `[ -n "${MIRROR_FROM:-}" ] ||` guard in front of the `build_image` check in [docker_build_push_lib.sh](../shscripts/docker_build_push_lib.sh). No other wrapper uses `MIRROR_FROM`.
3. Keep the registry-existence check of the three build refs in [my-jupyter-with-julia/docker_build_and_push.sh](../my-jupyter-with-julia/docker_build_and_push.sh); it still fails loudly if the upstream tag is missing.
4. Update the version-bump steps in [my-jupyter-with-julia/README.md](../my-jupyter-with-julia/README.md).
5. `my-latex-devcontainer/Dockerfile` also uses `okatsn/my-typst-space:v2026a`; point it to the official image as well.
