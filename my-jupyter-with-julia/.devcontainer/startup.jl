# ~/.julia/config/startup.jl

# References:
# [Automatically start with Julia](https://kristofferc.github.io/OhMyREPL.jl/latest/installation/#Automatically-start-with-Julia.)
# TerminalPager:
# - https://ronisbr.github.io/TerminalPager.jl/dev/
# - https://discourse.julialang.org/t/ann-terminalpager-jl-v0-5-0/104122
# Also see: [Customizing your IJulia environment](https://julialang.github.io/IJulia.jl/v1.22/manual/usage/#Customizing-your-IJulia-environment) that uses [Revise.jl](https://quarto.org/docs/computations/julia.html#revise.jl).
#
#
# !!! note
#     Docker compose keep existing files when mounting the volume to a container.
#     The file (startup.jl) is located in .julia, which is mounted as "volume". `COPY` this file in Dockerfile will take no effect if the volume already exists, unless one manually prune volume in advance. The same for all commands that are expected to change `Project.toml` and `Manifest.toml` in Dockerfile: changes won't persist when files of the same name already exist in the volume to be mounted.
#
#    The current solution: Manually run `helper/init.sh v1.xx` once a container is rebuild.


# !!! note "Best practices in interactive / REPL mode:"
#
# - Always launch julia with `julia --project` or `julia --project=@.`
#
# > Ref. https://gemini.google.com/app/dc4dbd0bfdba4ef1

# ==============================================================================
# 1. Early-stage tools (Revise must run before other code is evaluated)
# ==============================================================================
if isinteractive()
    try
        using Revise
    catch e
        @warn "startup.jl: Revise failed to load" exception=(e, catch_backtrace())
    end
end

# ==============================================================================
# 2. Interactive REPL hooks
# ==============================================================================
atreplinit() do repl
    # Isolated loader: ensures one failure does not abort other packages
    function safe_load(pkg::Symbol)
        try
            @eval using $pkg
        catch e
            @warn "startup.jl: Failed to load $pkg" exception=e
        end
    end

    # Defer non-critical UI hooks slightly to avoid Julia 1.12+ REPLExt race condition
    @async begin
        sleep(0.1) # 100ms is sufficient to let the REPL backend mount
        safe_load(:OhMyREPL)
        safe_load(:OkStartUp)
    end
end

# ==============================================================================
# 3. Lazy-loaded conveniences (prevents pre-loading heavy dependencies)
# ==============================================================================
# TerminalPager pulls in PrettyTables and StringManipulation; they are prone to conflicts caused by version inconsistency with the project environment.
# Instead of loading it at boot (which pollutes RAM and breaks project precompilation),
# this stub imports it on-demand the first time you invoke `pager()`.
function pager(args...; kwargs...)
    @eval using TerminalPager
    Base.invokelatest(TerminalPager.pager, args...; kwargs...)
end
