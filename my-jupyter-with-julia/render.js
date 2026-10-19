const fs = require('fs');
const mustache = require('mustache');

// Read the data file
const data = JSON.parse(fs.readFileSync('data.json', 'utf8'));

// Skill sets are not configured in data.json: every subdirectory of the host skillsets root is included.
const skillsetsRoot = `${process.env.HOME}/projects/my-agents/copilot/skillsets`;
if (!fs.existsSync(skillsetsRoot)) {
    throw new Error(`Skillsets root not found: ${skillsetsRoot}`);
}
const skillsets = fs.readdirSync(skillsetsRoot, { withFileTypes: true })
    .filter((e) => e.isDirectory() && !e.name.startsWith('.'))
    .map((e) => e.name)
    .sort();
if (skillsets.length === 0) {
    throw new Error(`No skill sets found in: ${skillsetsRoot}`);
}
data.skillsets_dirs = skillsets.map((name) => `/home/jovyan/skillsets/${name}`).join(',');

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
