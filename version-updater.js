const fs = require('fs');

const file = './package.json';

// Read package.json
const packageJson = JSON.parse(fs.readFileSync(file, 'utf8'));

// Extract version
const versionString = packageJson.version;
const [mainVersion, preRelease] = versionString.split('-');
const parts = mainVersion.split('.').map(Number);

if (parts.length !== 3) {
    console.error(`❌ Invalid version format: ${versionString}`);
    process.exit(1);
}

// Bump patch version (last digit)
parts[2] += 1;

// Build new version string
let newVersion = parts.join('.');
if (preRelease) {
    newVersion += `-${preRelease}`;
}

packageJson.version = newVersion;

// Write back to package.json
fs.writeFileSync(file, JSON.stringify(packageJson, null, 2) + '\n');

console.log(`✅ Version bumped to: ${newVersion}`);
