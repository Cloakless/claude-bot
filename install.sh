#!/bin/bash
set -e

# Configuration
INSTALL_DIR="/usr/local/lib/claude-bot"
VENV_DIR="$INSTALL_DIR/venv"
BIN_PATH="/usr/local/bin/claude"

# Create and set up install directory
sudo mkdir -p "$INSTALL_DIR"
sudo cp -r ./* "$INSTALL_DIR/"

# Create virtual environment
sudo python3 -m venv "$VENV_DIR"
sudo "$VENV_DIR/bin/pip" install anthropic

# Create executable wrapper
cat << EOF | sudo tee "$BIN_PATH"
#!/bin/bash
source "$VENV_DIR/bin/activate"
python "$INSTALL_DIR/tool.py" "\$@"
EOF

sudo chmod +x "$BIN_PATH"

echo "Tool successfully installed. Run 'claude' to start."
