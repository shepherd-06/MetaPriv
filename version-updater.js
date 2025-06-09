const fs = require('fs');
const { execSync } = require('child_process');

const file = './package.json';

// Get current Git branch
let branch = 'unknown';
try {
    branch = execSync('git rev-parse --abbrev-ref HEAD').toString().trim();
} catch (err) {
    console.error('❌ Failed to get current git branch:', err.message);
    process.exit(1);
}

// Read package.json
const packageJson = JSON.parse(fs.readFileSync(file, 'utf8'));

// Extract version
const versionString = packageJson.version;
const [mainVersion] = versionString.split('-');
const parts = mainVersion.split('.').map(Number);

if (parts.length !== 3) {
    console.error(`❌ Invalid version format: ${versionString}`);
    process.exit(1);
}

// Bump patch version
parts[2] += 1;

// Determine suffix
const suffix = branch === 'master' ? 'alpha' : 'nightly';

// Build new version string
const newVersion = `${parts.join('.')}-${suffix}`;
packageJson.version = newVersion;

// Write back to package.json
fs.writeFileSync(file, JSON.stringify(packageJson, null, 2) + '\n');

console.log(`✅ Version bumped to: ${newVersion} (branch: ${branch})`);
