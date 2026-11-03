const fs = require('fs');
const path = require('path');
const mustache = require('mustache');

// Usage: node render.js [--data data.json] [--out DIR]; renders into DIR/.devcontainer/ (defaults: `data.json` and `.` in the current directory)
const args = process.argv.slice(2);
const argOf = (flag, fallback) => (args.includes(flag) ? args[args.indexOf(flag) + 1] : fallback);
const dataFile = argOf('--data', 'data.json');
const outDir = argOf('--out', '.');

// Read the data file
const data = JSON.parse(fs.readFileSync(dataFile, 'utf8'));

// Mustache has no "last item" test, so derive a comma-separated list: `skill_family_items` carries a trailing `sep` per entry.
const skillFamilies = data.skill_families || [];
const view = {
    ...data,
    skill_family_items: skillFamilies.map((name, i) => ({
        name,
        sep: i < skillFamilies.length - 1 ? ',' : '',
    })),
};

// [template, output] pairs
const targets = [
    ['devcontainer.mustache', '.devcontainer/devcontainer.json'],
    ['docker-compose.mustache', '.devcontainer/docker-compose.yml'],
    ['preflight.sh.mustache', '.devcontainer/preflight.sh'],
];

fs.mkdirSync(path.join(outDir, '.devcontainer'), { recursive: true });
for (const [template, output] of targets) {
    const rendered = mustache.render(fs.readFileSync(path.join(__dirname, template), 'utf8'), view);
    fs.writeFileSync(path.join(outDir, output), rendered);
}

console.log('Files has been generated');
