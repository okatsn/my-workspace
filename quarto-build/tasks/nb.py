# from invoke import task

# @task
# def lab(ctx):
#     """Run jupyter lab at notebooks directory."""
#     ctx.run("jupyter lab --notebook-dir=notebooks --port=8888", pty=True)

# @task
# def notebook(ctx):
#     """Run jupyter notebook at notebooks directory."""
#     ctx.run("jupyter notebook --notebook-dir=notebooks --port=8888", pty=True)

# @task
# def pluto(ctx):
#     """Run Pluto.jl at notebooks directory."""
#     ctx.run("cd notebooks && julia --project=@. -e 'using Pluto; Pluto.run()'", pty=True)

# @task
# def convert(ctx, f, enableScroll="False", to="html", other="--post serve --no-input"): # `invoke --help nb.convert` to get help
#     """
#     `convert(ctx, f, enableScroll="False", to="html", other="--post serve --no-input")`
#     converts the target .ipynb file `f` to html without input code by default.
#     For option `other`, check the document of jupyter's `nbconvert`.


#     # Example,
#     Convert .ipynb notebook to html using default settings:
#     - `inv nb.convert ./notebooks/mynb.ipynb`, which is equivalent to `jupyter nbconvert ./notebooks/mynb.ipynb --to html --post serve --no-input`

#     Convert .ipynb notebook to reveal.jl's slides where scroll is enabled:
#     - `inv nb.convert ./notebooks/mynb.ipynb --to=slides --enableScroll=True`, which is equivalent to `jupyter nbconvert ./notebooks/mynb.ipynb --to slides --SlidesExporter.reveal_scroll=True --post serve --no-input`

#     Convert .ipynb notebook to html with input code:
#     - `inv nb.convert ./notebooks/mynb.ipynb --other=""`, which is equivalent to `jupyter nbconvert ./notebooks/mynb.ipynb --to html`
#     """
#     command = "jupyter nbconvert {} --to {} --SlidesExporter.reveal_scroll={} {}".format(f, to, enableScroll, other)
#     ctx.run(command)

#     # also see https://stackoverflow.com/questions/53186944/accommodating-large-slides-in-jupyter-presentation
