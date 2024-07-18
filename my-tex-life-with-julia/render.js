const fs = require('fs');
const mustache = require('mustache');

// Read the template file
const template = fs.readFileSync('template.mustache', 'utf8');

// Read the data file
const data = JSON.parse(fs.readFileSync('data.json', 'utf8'));

// Render the template with the data
const output = mustache.render(template, data);

// Write the output to an HTML file
fs.writeFileSync('output.html', output);

console.log('HTML file has been generated: output.html');
