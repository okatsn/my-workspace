# Q

I manage my environment as the following 3-stage building process.
Consider the scenario to update julia from , for example, from 1.12.6 to 1.13, I need to do the followings:

1. Update ARG `VARIANT` to "1.13.1" and `JULIA_PROJECT` to  "v1.13" in Dockerfile 1.
2. Run `. docker_build_and_push.sh v1.13-2026d.0 v1.13-2026d latest` in the directory of `julia-debian-build`.
3. Update "v1.12-2026c" in `FROM okatsn/my-julia-build:v1.12-2026c AS build-julia` to "v1.13-2026d" in Dockerfile 2.
4. Run `. docker_build_and_push.sh v2026d v2026d.0 latest`
5. Update `FROM okatsn/my-jupyter-with-julia:v2026c.2` to "v2026d.0" in Dockerfile 3 (then distribute Dockerfile 3 as the final product).

Although the current step-by-step workflow is quite useful: we manually run can wait for the results before commit the hard-coded version into Dockerfiles. This is robust but requires many human's care. I'm wondering whether I can streamline this "julia version update" process without introduce too-complicate scripts, while keeping the same or better level of robustness (and fail fast). In my initial thought, for example, there might be a robust solution that the julia version info is stored in a json/yaml file, and three Dockerfiles can be updated via a small helper script? Is the industry doing such a very tiny "Continuous Integration" things in a similar way?


# A

Yes. What you have is already a small **release/promotion pipeline**:

**build → test → publish → use the published artifact downstream → test → publish → promote final Dockerfile**

That is a very normal CI/CD pattern. The main improvement I would make is **not** to automate textual replacement across three Dockerfiles. Instead, make the versions build parameters and keep one tiny source-of-truth file.

For your setup, I would use a simple `.env`-style file rather than JSON/YAML. Docker Compose understands env files natively, supports multiple `--env-file` files, and even supports fail-fast required-variable expressions such as `${VAR:?error}`. [Docker Documentation](https://docs.docker.com/reference/compose-file/interpolation/?utm_source=chatgpt.com)

## The design I would use

Something like:

```text
release.env
release-julia.sh

julia-debian-build/
    Dockerfile
    compose.yaml

my-jupyter-with-julia/
    Dockerfile
    compose.yaml

final/
    Dockerfile
```

And `release.env` contains only the values a human actually decides:

```dotenv
JULIA_VERSION=1.13.1
RELEASE=2026d

JULIA_BUILD_REV=0
JUPYTER_BUILD_REV=0
```

Everything else can be derived:

```text
JULIA_VERSION       = 1.13.1
JULIA_MINOR         = 1.13
JULIA_PROJECT       = v1.13

stage 1 immutable   = v1.13-2026d.0
stage 1 channel     = v1.13-2026d

stage 2 immutable   = v2026d.0
stage 2 channel     = v2026d
```

So there is no opportunity to accidentally write `1.13.1` in one place and `v1.12` somewhere else.

---

# 1. Parameterize Dockerfile 1

Instead of:

```dockerfile
ARG VARIANT="1.12.6"
ARG JULIA_PROJECT="v1.12"
```

I would make these required build inputs:

```dockerfile
ARG VARIANT
ARG JULIA_PROJECT

RUN test -n "$VARIANT" \
    && test -n "$JULIA_PROJECT"

ENV JULIA_PROJECT=${JULIA_PROJECT}
```

Then in Compose:

```yaml
services:
  jbuild:
    build:
      context: .
      args:
        VARIANT: ${JULIA_VERSION:?JULIA_VERSION is required}
        JULIA_PROJECT: ${JULIA_PROJECT:?JULIA_PROJECT is required}
```

The `${VAR:?message}` syntax causes Compose to stop immediately if the variable is absent or empty, which is useful here. [Docker Documentation](https://docs.docker.com/reference/compose-file/interpolation/?utm_source=chatgpt.com)

Your orchestration script derives:

```bash
JULIA_MINOR="${JULIA_VERSION%.*}"
export JULIA_PROJECT="v${JULIA_MINOR}"
```

Thus Dockerfile 1 doesn't contain a release version anymore.

### One additional fail-fast improvement

Your current Julia download uses:

```dockerfile
curl -L ... | tar zxf -
```

I'd prefer:

```dockerfile
RUN curl -fsSL \
    "https://julialang-s3.julialang.org/bin/linux/x64/$(echo "$VARIANT" | cut -d. -f1,2)/julia-${VARIANT}-linux-x86_64.tar.gz" \
    -o /tmp/julia.tar.gz \
    && tar zxf /tmp/julia.tar.gz -C "$JULIA_PATH" --strip=1 \
    && rm /tmp/julia.tar.gz \
    && ln -fs "$JULIA_PATH/bin/julia" /usr/local/bin/julia \
    && julia --version
```

`curl -f` makes HTTP errors fail rather than quietly producing an error page.

You can later add checksum verification if you want another layer of robustness.

---

# 2. Parameterize Dockerfile 2's `FROM`

This is where Docker's global `ARG` feature is particularly useful.

Instead of:

```dockerfile
FROM okatsn/my-julia-build:v1.12-2026c AS build-julia
```

use:

```dockerfile
ARG JULIA_BUILD_REF
FROM ${JULIA_BUILD_REF} AS build-julia

FROM okatsn/my-quarto-build:v1.8-2026a AS build-quarto
FROM okatsn/my-typst-space:v2026a AS build0
FROM quay.io/jupyter/minimal-notebook:ubuntu-24.04
```

Docker explicitly permits `ARG` before the first `FROM`, and those arguments can be used in `FROM`. [docs.docker.com](https://docs.docker.com/reference/dockerfile?utm_source=chatgpt.com)

Then build with:

```bash
export JULIA_BUILD_REF="okatsn/my-julia-build:v1.13-2026d.0"
```

This means Dockerfile 2 never needs to be edited during a Julia upgrade.

## Important: use `.0`, not the moving `v1.13-2026d` tag here

This is one thing I would change from your existing process.

You currently have:

```dockerfile
FROM okatsn/my-julia-build:v1.12-2026c
```

where `v1.12-2026c` can later be moved from `.0` to `.1`.

That means rebuilding an old Dockerfile might silently consume a different Julia build.

Instead, downstream dependencies should use:

```text
v1.13-2026d.0
```

while:

```text
v1.13-2026d
latest
```

are convenience/channel aliases for humans.

Even stronger would be a registry digest:

```dockerfile
FROM okatsn/my-julia-build@sha256:...
```

but I think immutable `.0`, `.1`, etc. tags are a good complexity/robustness tradeoff for your setup. Docker's registry inspection tools can expose the image digest if you eventually want to move to that model. [Docker Documentation](https://docs.docker.com/reference/cli/docker/buildx/imagetools/inspect/?utm_source=chatgpt.com)

---

# 3. Keep only Dockerfile 3's default as the final release record

Because Dockerfile 3 is something you actually distribute as the product, I think having a visible pinned version there is desirable.

I'd change:

```dockerfile
FROM okatsn/my-jupyter-with-julia:v2026c.2
```

into:

```dockerfile
ARG BASE_IMAGE="okatsn/my-jupyter-with-julia:v2026d.0"
FROM ${BASE_IMAGE}
```

The default remains self-contained:

```bash
docker build .
```

still works.

But an advanced user can override it:

```bash
docker build \
  --build-arg BASE_IMAGE=okatsn/my-jupyter-with-julia:v2026d.1 \
  .
```

And importantly, **this becomes the only Dockerfile line that your release process actually modifies**.

I would deliberately keep that one modification because it serves as your final promotion record:

> "This distributed Dockerfile is based on the successfully tested `v2026d.0` image."

---

# 4. One small release script controls the gates

Your `release-julia.sh` doesn't need to know how to rewrite complicated Dockerfiles.

Conceptually it does:

```text
read release.env
        │
        ▼
validate configuration
        │
        ▼
derive v1.13 / v1.13-2026d.0 / v2026d.0
        │
        ▼
build stage 1 locally
        │
        ▼
smoke-test stage 1
        │
        ├── FAIL → stop
        ▼
push v1.13-2026d.0
        │
        ▼
verify registry image exists
        │
        ▼
push aliases v1.13-2026d + latest
        │
        ▼
build stage 2 FROM v1.13-2026d.0
        │
        ▼
smoke-test stage 2
        │
        ├── FAIL → stop
        ▼
push v2026d.0
        │
        ▼
verify registry image exists
        │
        ▼
push alias v2026d (+ latest if desired)
        │
        ▼
update Dockerfile 3 → v2026d.0
        │
        ▼
build/test Dockerfile 3
        │
        ├── FAIL → don't commit
        ▼
ready to commit/distribute
```

That is your existing manual safety model, encoded mechanically.

---

# 5. Make the immutable tag truly immutable

This is one of the most useful safeguards you can add.

Before publishing:

```bash
IMAGE="okatsn/my-julia-build:v1.13-2026d.0"

if docker buildx imagetools inspect "$IMAGE" >/dev/null 2>&1; then
    echo "ERROR: immutable tag already exists: $IMAGE" >&2
    exit 1
fi
```

Then `.0` is never accidentally overwritten.

If it needs rebuilding, bump:

```dotenv
JULIA_BUILD_REV=1
```

and get:

```text
v1.13-2026d.1
```

Docker's `buildx imagetools inspect` operates against the registry, so it is useful both for existence checks and later digest verification. [Docker Documentation](https://docs.docker.com/reference/cli/docker/buildx/imagetools/inspect/?utm_source=chatgpt.com)

Your aliases can still move:

```text
v1.13-2026d → v1.13-2026d.1
latest       → v1.13-2026d.1
```

That's a clean distinction:

| Tag | Meaning | Mutable? |
|---|---|---:|
| `v1.13-2026d.0` | exact artifact | **No** |
| `v1.13-2026d.1` | exact artifact | **No** |
| `v1.13-2026d` | current build in this release | Yes |
| `latest` | current overall build | Yes |

I would apply exactly the same rule to `v2026d.0`.

---

# 6. Test locally before pushing

This is where I would improve your existing `docker_build_and_push.sh`.

Right now the script conceptually does:

```text
build → push
```

I'd make it:

```text
build → test → push
```

For stage 1, even a tiny smoke test gives you a strong gate:

```bash
docker run --rm \
    okatsn/my-julia-build:candidate \
    julia --startup-file=no -e '
        @assert VERSION == v"1.13.1"
        @assert ENV["JULIA_PROJECT"] == "v1.13"
        println("Julia stage OK")
    '
```

Stage 2 could test the integration points you actually care about:

```bash
docker run --rm \
    okatsn/my-jupyter-with-julia:candidate \
    bash -lc '
        set -e
        julia --version
        quarto --version
        typst --version
        dvc --version
    '
```

You could make the Julia assertion exact there too.

Then the release script only publishes if those commands succeed.

This is better than merely waiting to see whether Docker itself successfully built the image, because a successful Docker build doesn't necessarily mean your runtime integration works.

---

# 7. I would also change how you invoke the shell script

You currently use:

```bash
. docker_build_and_push.sh ...
```

That **sources** the script into your current shell.

I'd use:

```bash
./docker_build_and_push.sh ...
```

instead.

Especially since the script contains:

```bash
set -e
trap ...
exit 1
```

sourcing it means shell options, variables, traps, and `exit` behavior can affect your interactive parent shell.

For a build/release program, execution as a separate process is cleaner.

And I'd change:

```bash
set -e
```

to:

```bash
set -Eeuo pipefail

trap 'rc=$?; echo "ERROR: line $LINENO: $BASH_COMMAND (exit $rc)" >&2' ERR
```

You can retain your interactive error prompt if you like.

---

# 8. Your source-of-truth file can stay extremely small

I would **not** write this:

```yaml
julia:
  version: 1.13.1
  project: v1.13
  build:
    immutable: v1.13-2026d.0
    stable: v1.13-2026d

jupyter:
  immutable: v2026d.0
  stable: v2026d
```

because now you've simply created several more values that humans can make inconsistent.

Prefer:

```dotenv
JULIA_VERSION=1.13.1
RELEASE=2026d
JULIA_BUILD_REV=0
JUPYTER_BUILD_REV=0
```

and derive everything else.

For example:

```bash
JULIA_MINOR="${JULIA_VERSION%.*}"

JULIA_PROJECT="v${JULIA_MINOR}"

JULIA_BUILD_TAG="v${JULIA_MINOR}-${RELEASE}.${JULIA_BUILD_REV}"
JULIA_BUILD_CHANNEL="v${JULIA_MINOR}-${RELEASE}"

JUPYTER_BUILD_TAG="v${RELEASE}.${JUPYTER_BUILD_REV}"
JUPYTER_BUILD_CHANNEL="v${RELEASE}"
```

Add a validation guard:

```bash
[[ "$JULIA_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || {
    echo "Invalid JULIA_VERSION: $JULIA_VERSION" >&2
    exit 2
}

[[ "$RELEASE" =~ ^[0-9]{4}[a-z]$ ]] || {
    echo "Invalid RELEASE: $RELEASE" >&2
    exit 2
}
```

That's enough.

---

# 9. Your resulting upgrade becomes very small

For Julia 1.13.1, the human procedure becomes:

Edit:

```diff
 JULIA_VERSION=1.12.6
-RELEASE=2026c
+JULIA_VERSION=1.13.1
+RELEASE=2026d

 JULIA_BUILD_REV=0
 JUPYTER_BUILD_REV=0
```

Actually, assuming those are separate existing lines:

```diff
-JULIA_VERSION=1.12.6
-RELEASE=2026c
+JULIA_VERSION=1.13.1
+RELEASE=2026d
```

Then:

```bash
./release-julia.sh
```

The script prints something like:

```text
Julia version:       1.13.1
Julia project:       v1.13

Stage 1:
  immutable:         okatsn/my-julia-build:v1.13-2026d.0
  channel:           okatsn/my-julia-build:v1.13-2026d

Stage 2:
  immutable:         okatsn/my-jupyter-with-julia:v2026d.0
  channel:           okatsn/my-jupyter-with-julia:v2026d

Final Dockerfile:
  base:              okatsn/my-jupyter-with-julia:v2026d.0
```

And then works its way through the gates.

That reduces your five manual version-changing/build steps to essentially:

```text
edit two values
        +
run one command
        +
review the final git diff
```

without removing the sequential validation that makes your current process reliable.

---

## Where CI enters

What I've described is already a **local CI pipeline**, in spirit.

Moving it to GitHub Actions later is almost mechanical:

```text
build-julia
    ↓ needs
test-and-push-julia
    ↓ needs
build-jupyter
    ↓ needs
test-and-push-jupyter
    ↓ needs
prepare-final-dockerfile
```

GitHub Actions has explicit job dependencies through `needs`; if a prerequisite job fails, dependent jobs are skipped by default. [GitHub Docs](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-jobs?utm_source=chatgpt.com)

So yes, industry CI systems do essentially what you're doing manually now: **an artifact is built once, validated, assigned an immutable identity, and only then promoted to downstream stages.**

I wouldn't jump to GitHub Actions immediately, though. A ~50–100-line local Bash release driver is probably the sweet spot for your current scale. Once that workflow proves stable, CI can simply execute the same script rather than reimplementing all its logic in YAML.

---

## Renovate is a possible later step, but not the first thing I'd add

Renovate can already detect Docker image references in Dockerfiles and propose upgrades, and custom regex managers exist for nonstandard version locations. [Renovate 文件](https://docs.renovatebot.com/docker/?utm_source=chatgpt.com)

But with your deliberately custom tags:

```text
v1.13-2026d.0
v2026d.0
```

and your multi-stage promotion semantics, I'd **not** make Renovate responsible for the whole release process.

At most I'd eventually let it say:

> Julia 1.13.2 is available.

Then *you* decide to update:

```dotenv
JULIA_VERSION=1.13.2
```

and your release pipeline does the rest.

---

## The one architectural change I'd prioritize

If you change nothing else, change this relationship:

```text
Dockerfile 2
    ↓
FROM ...:v1.13-2026d       ← mutable
```

to:

```text
Dockerfile 2 / build parameter
    ↓
FROM ...:v1.13-2026d.0     ← immutable
```

and similarly ensure Dockerfile 3 consumes:

```text
v2026d.0
```

rather than `v2026d`.

Then treat:

```text
v1.13-2026d
v2026d
latest
```

as aliases only, never as inputs to another released artifact.

That gives you the nice property:

> **Every released image can be traced to the exact released images from which it was constructed.**

So I think your proposed central-version idea is right, with one adjustment: **use the central file as build input rather than using it primarily to rewrite Dockerfiles.** Let Docker `ARG`, Compose interpolation, immutable tags, and a small gated shell script do most of the work. That is both less code and more robust than regex-editing three Dockerfiles.