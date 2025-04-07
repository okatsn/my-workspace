const fs = require('fs');
const mustache = require('mustache');

// Read the template file
const template_for_repo_a = fs.readFileSync('trigger_repo_b.mustache', 'utf8');
const template_for_repo_b = fs.readFileSync('to_be_triggered_by_repo_a.mustache', 'utf8');


// Read the data file
const data = JSON.parse(fs.readFileSync('data.json', 'utf8'));

// Render the template with the data
const output_to_repo_a = mustache.render(template_for_repo_a, data);
const output_to_repo_b = mustache.render(template_for_repo_b, data);

// Write the output to an HTML file
fs.writeFileSync('.github_A/trigger_repo_b.yml', output_to_repo_a);
fs.writeFileSync('.github_B/to_be_triggered_by_repo_a.yml', output_to_repo_b);

console.log('Files has been generated');
