# Working with two repositories

## About submodules

### Initialize submodules

When you clone a repo in a fresh new local directory, without initiation there will be no information in `.git/config` and no referencing files in `.git/modules`

```bash
# Initialize without clone
git submodule init 

# Initialize and clone
git submodule update --init
```



### Add submodules

```bash
# Add a submodule of name sub-something
git submodule add -b main https://github.com/okatsn/SomeProject.git optional-custom-project-name
git commit -m "Add MyTeXLife as submodule sub-something."
```

> `-b main` explicitly specify the branch to be tracked when you run `update --remote`.

### Keep submodules updated to remote

Update all submodules:

```
git submodule update --remote
```

Update only a specific submodule:

```
git submodule update --remote <your_submodule_name>
```


To make your submodule keep in track with a specific branch when update, `main` for example, add `branch = main` in .gitmodule:

```
# .gitmodule file

[submodule "<your_submodule_name>"]
	path = <your_submodule_name>
	url = https://github.com/okatsn/<your_submodule_name>.git
	branch = main
    # The submodule's HEAD will always checkout to main after `git submodule update --remote`

```


> Noted that `update` will typically result in a detached head unless additional flag `--rebase` or `--merge` is specified.
> See: 
> - https://git-scm.com/docs/git-submodule#_options
> - https://stackoverflow.com/questions/19619747/git-submodule-update-remote-vs-git-pull/19621245#19621245


### Edit local submodule

Saying a repository was added as the submodule of "sub-something", and I have done some new modifications:

```bash
cd sub-something
git checkout master # or main, depending on the branch
git pull origin master # or the branch you are tracking
cd ..
git add sub-something
git commit -m "Update submodule to latest original source"

```

### Remove 

Referring [myusuf3/delete_git_submodule.md](https://gist.github.com/myusuf3/7f645819ded92bda6677), the submodule contents and configurations are located in the following, and our goal is to clear them all.
- An entry in `.git/config`
- An entry in `.gitmodules`
- A folder in the workspace.



Method 1: 

```bash
# this is the same as remove the folder and stage the change.
git rm sub-something

# remove manually the entry using `vi` in the followings:
vi .gitmodule 
vi .git/config

# remove left
rm -rf .git/modules/sub-something
```

[Method 2](https://stackoverflow.com/questions/76166810/how-to-delete-a-git-submodule-locally):

```bash
# Automatically remove the entries 
git submodule deinit -f sub-something

# this is the same as remove the folder and stage the change.
git rm sub-something

# remove left
rm -rf .git/modules/sub-something
```

### Other tips

If you manually change the url in .gitmodules, please run `git submodule sync`. [This updates .git/config](https://stackoverflow.com/questions/11637175/swap-git-submodule-with-own-fork).


## Merge two repositories as a squash

```
git remote add RepoB <url-of-RepoB>
git fetch RepoB
git checkout -b merge-repoB
git merge --allow-unrelated-histories --squash RepoB/main
git commit -m "Merged RepoB without preserving history"
```