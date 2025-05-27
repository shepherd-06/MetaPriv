#!/bin/bash

set -e

# Config
REQUIRED_NODE_VERSION="v24.0.1"
REQUIRED_NPM_VERSION="11.3.0"
INSTALL_DIR="$HOME/Library/MetaPriv"
GIT_REPO="https://github.com/shepherd-06/MetaPriv.git"
GIT_TARGET_BRANCH="dev"  # Change this if you want a different branch or tag

# Function to compare versions
version_ge() {
  [ "$(printf '%s\n' "$@" | sort -V | head -n 1)" != "$1" ]
}

echo "🔍 Checking for Node.js..."

if command -v node >/dev/null 2>&1; then
  INSTALLED_NODE_VERSION=$(node -v)
  echo "✅ Node.js is installed: $INSTALLED_NODE_VERSION"
else
  echo "❌ Node.js not found. Installing..."
  curl -o node.pkg https://nodejs.org/dist/v24.0.1/node-v24.0.1.pkg
  sudo installer -pkg node.pkg -target /
  rm node.pkg
fi

echo "🔍 Checking for npm..."

if command -v npm >/dev/null 2>&1; then
  INSTALLED_NPM_VERSION=$(npm -v)
  echo "✅ npm is installed: $INSTALLED_NPM_VERSION"
else
  echo "❌ npm not found. Please install it manually."
  exit 1
fi

# Clone or update repository
if [ -d "$INSTALL_DIR/.git" ]; then
  echo "📁 MetaPriv already exists at $INSTALL_DIR"
  cd "$INSTALL_DIR"
  
  CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
  echo "🔍 Current branch: $CURRENT_BRANCH"

  if [ "$CURRENT_BRANCH" != "$GIT_TARGET_BRANCH" ]; then
    echo "🔀 Switching to $GIT_TARGET_BRANCH branch..."
    git fetch
    git checkout "$GIT_TARGET_BRANCH"
    git pull
  else
    echo "✅ Already on $GIT_TARGET_BRANCH branch. Pulling latest..."
    git pull
  fi

else
  echo "📥 Cloning MetaPriv ($GIT_TARGET_BRANCH) to $INSTALL_DIR"
  git clone --branch "$GIT_TARGET_BRANCH" --depth 1 "$GIT_REPO" "$INSTALL_DIR"
fi

# Install dependencies
echo "📦 Installing npm packages..."
cd "$INSTALL_DIR"
npm install

# Build frontend
cd "$INSTALL_DIR/frontend"
echo "📦 Installing npm packages for FrontEnd..."
npm install
echo "🛠️ Building frontend..."
npm run build

cd "$INSTALL_DIR"

# Create desktop shortcut
DESKTOP_SHORTCUT="$HOME/Desktop/MetaPriv.sh"
if [ ! -f "$DESKTOP_SHORTCUT" ]; then
  echo "🔗 Creating desktop shortcut at $DESKTOP_SHORTCUT"
  cat <<EOL > "$DESKTOP_SHORTCUT"
#!/bin/bash
cd "$INSTALL_DIR"
npm start
EOL
  chmod +x "$DESKTOP_SHORTCUT"
else
  echo "✅ Desktop shortcut already exists."
fi

echo "🎉 MetaPriv is ready! Use the shortcut on your desktop or run:"
echo "🚀 Enjoy using MetaPriv!"