const fs = require('fs');
const mustache = require('mustache');

// Read the data file
const data = JSON.parse(fs.readFileSync('data.json', 'utf8'));

// [template, output] pairs
const targets = [
    ['devcontainer.mustache', '.devcontainer/devcontainer.json'],
    ['docker-compose.mustache', '.devcontainer/docker-compose.yml'],
    ['preflight.sh.mustache', '.devcontainer/preflight.sh'],
];

for (const [template, output] of targets) {
    fs.writeFileSync(output, mustache.render(fs.readFileSync(template, 'utf8'), data));
}

console.log('Files has been generated');
