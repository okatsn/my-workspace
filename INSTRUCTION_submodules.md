## More about submodules


### Update
```bash
cd sub-something
git checkout master # or main, depending on the branch
git pull origin master # or the branch you are tracking
cd ..
git add sub-something
git commit -m "Update submodule to latest original source"

```
### Add and remove submodules
CHECKPOINT: https://chat.openai.com/c/30c3b844-d39a-4ab2-b6c9-3c92b24484ff



```bash
# Add a submodule of name sub-something
git submodule add https://github.com/okatsn/MyTeXLife.git sub-something
git commit -m "Add MyTeXLife as submodule sub-something."

```

Remove

```bash
# this is the same as remove the folder and stage the change.
git rm sub-something

# remove manually the entry using `vi` in the followings:
vi .gitmodule 
vi .git/config

# remove left
rm -rf .git/modules/sub-something
```