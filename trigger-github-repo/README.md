# README

## How it works

## Setup


Modify [data.json](data.json).

```bash
cd trigger-github-repo
```


```bash
node render.js
```

Restore changes

```bash
git restore .github_A/trigger_repo_b.yml 
git restore .github_B/to_be_triggered_by_repo_a.yml 
git restore data.json
```

## Authentication

To trigger a workflow in Repo B from Repo A, the action needs a token that has permissions in Repo B.
The standard way to achieve this is using a Personal Access Token (PAT):

### Create a PAT

Go to the GitHub account settings of a user who has write access to **Repo B**.

1. Navigate to Developer settings > Personal access tokens > Tokens (classic) or Fine-grained tokens.
2. Generate a new fine-grained token: 
   1. Give it a name. 
   2. Select Repo B as the target repository. 
   3. Grant it "Read and Write" permissions for Actions
   4. Grant it "Read and Write" permissions for Contents
3. Copy the generated token immediately


Store the PAT as a Secret in **Repo A**:

1. Go to Repo A's settings on GitHub.
1. Navigate to Secrets and variables > Actions.
1. Click New repository secret.
1. Name the secret something like `REPO_B_PAT`.
1. Paste the PAT you copied into the Value field.
1. Click Add secret.