# [Customizing your IJulia environment](https://julialang.github.io/IJulia.jl/v1.22/manual/usage/#Customizing-your-IJulia-environment) that uses [Revise.jl](https://quarto.org/docs/computations/julia.html#revise.jl).
try
    @eval using Revise
catch e
    @warn "Revise init" exception = (e, catch_backtrace())
end