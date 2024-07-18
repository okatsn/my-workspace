- [README](#readme)
  - [Requirement](#requirement)
  - [To create a mustache project](#to-create-a-mustache-project)
  - [To use the mustache template](#to-use-the-mustache-template)


# README
For how to use mustache.

## Requirement

```bash
sudo apt update
sudo apt install nodejs npm -y
```

## To create a mustache project

- Initiate a Node.js project of Mustache:
  ```bash
  npm init -y
  npm install mustache
  ```
- Install Mustache: `npm install mustache`.
- Create the file `template.mustache`.
- Create the files `render.js` script and `data.json` for variables.



## To use the mustache template

(in continuation to [To create a mustache project](#to-create-a-mustache-project))

- Set variables in `data.json`
- Run `node render.js` in the directory of the Mustache project.
