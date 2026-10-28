const fs = require('fs');
const mustache = require('mustache');

// Read the data file
const data = JSON.parse(fs.readFileSync('data.json', 'utf8'));

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

for (const [template, output] of targets) {
    fs.writeFileSync(output, mustache.render(fs.readFileSync(template, 'utf8'), view));
}

console.log('Files has been generated');
