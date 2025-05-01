# README

## Getting Started

1. Open `my-workspace/my-ojs-playground` in WSL
2. `Ctrl + P` in VSCode to `Dev Containers: Reopen in container`
3. See https://observablehq.com/framework/getting-started for tutorial.

# CHECKPOINT:

- [ ] Add git auto-completion in Dockerfile. For container settings, see [this](https://gemini.google.com/app/1dd1a4741a3258f9).

## Trouble shooting

### Troubleshooting Browser Access Issues in Containerized Environment

If in your browser shows such messages, 

```
The site could be temporarily unavailable or too busy. Try again in a few moments.
If you are unable to load any pages, check your computer’s network connection.
If your computer or network is protected by a firewall or proxy, make sure that Firefox is permitted to access the web.
```


`npm run dev -- --host 0.0.0.0` instead.

Explain: 

- When bound to 127.0.0.1, the server is only accessible from within the container
- When bound to 0.0.0.0, the server becomes accessible from outside the containe