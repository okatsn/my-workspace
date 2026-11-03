const fs = require('fs');
const path = require('path');
const mustache = require('mustache');

// Usage: node render.js [--data data.json] [--out DIR]; renders into DIR/.devcontainer/ (defaults: `data.json` and `.` in the current directory)
const args = process.argv.slice(2);
const argOf = (flag, fallback) => (args.includes(flag) ? args[args.indexOf(flag) + 1] : fallback);
const dataFile = argOf('--data', 'data.json');
const outDir = argOf('--out', '.');

// Read the template files (relative to this script)
const template_devcontainer = fs.readFileSync(path.join(__dirname, 'devcontainer.mustache'), 'utf8');
const template_docker_compose = fs.readFileSync(path.join(__dirname, 'docker-compose.mustache'), 'utf8');

// Read the data file
const data = JSON.parse(fs.readFileSync(dataFile, 'utf8'));

// Render the templates with the data
const output_devcontainer = mustache.render(template_devcontainer, data);
const output_docker_compose = mustache.render(template_docker_compose, data);

// Write the rendered files to DIR/.devcontainer/
fs.mkdirSync(path.join(outDir, '.devcontainer'), { recursive: true });
fs.writeFileSync(path.join(outDir, '.devcontainer/devcontainer.json'), output_devcontainer);
fs.writeFileSync(path.join(outDir, '.devcontainer/docker-compose.yml'), output_docker_compose);

console.log('Files have been generated');
