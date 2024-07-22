const fs = require('fs');
const mustache = require('mustache');

// Read the template file
const template_devcontainer = fs.readFileSync('devcontainer.mustache', 'utf8');
const template_docker_compose = fs.readFileSync('docker-compose.mustache', 'utf8');


// Read the data file
const data = JSON.parse(fs.readFileSync('data.json', 'utf8'));

// Render the template with the data
const output_devcontainer = mustache.render(template_devcontainer, data);
const output_docker_compose = mustache.render(template_docker_compose, data);

// Write the output to an HTML file
fs.writeFileSync('.devcontainer/devcontainer.json', output_devcontainer);
fs.writeFileSync('.devcontainer/docker-compose.yml', output_docker_compose);

console.log('Files has been generated');
