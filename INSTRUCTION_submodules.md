## More about submodules

### Add submodules

```bash
# Add a submodule of name sub-something
git submodule add https://github.com/okatsn/MyTeXLife.git sub-something
git commit -m "Add MyTeXLife as submodule sub-something."
```

### Keep submodules updated
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