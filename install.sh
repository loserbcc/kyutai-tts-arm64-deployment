#!/bin/bash
# Kyutai TTS ARM64 Automated Installer
# For NVIDIA DGX Spark (Grace Hopper) and similar ARM64+CUDA systems

set -e  # Exit on error

echo "🚀 Kyutai TTS ARM64 Installation Script"
echo "========================================"
echo ""

# Check if running on ARM64
if [ "$(uname -m)" != "aarch64" ]; then
    echo "❌ This script is for ARM64 systems only"
    exit 1
fi

# Check for NVIDIA GPU
if ! command -v nvidia-smi &> /dev/null; then
    echo "❌ nvidia-smi not found. This script requires NVIDIA GPU"
    exit 1
fi

echo "✓ ARM64 system detected"
echo "✓ NVIDIA GPU found: $(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)"
echo ""

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt update
sudo apt install -y libopus-dev cmake git git-lfs python3-dev python3-venv

# Install uv if not present
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv ~/kyutai-test

# Activate and install PyTorch with CUDA
echo "🔥 Installing PyTorch with CUDA 13.0..."
source ~/kyutai-test/bin/activate
uv pip install torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/nightly/cu130

# Verify CUDA
echo "🔍 Verifying CUDA..."
python3 -c "import torch; assert torch.cuda.is_available(), 'CUDA not available!'"
echo "✓ CUDA working!"

# Clone and patch Moshi
echo "📥 Cloning Moshi repository..."
cd ~
git clone https://github.com/kyutai-labs/moshi.git moshi-repo
cd moshi-repo/moshi

# Apply ARM64 patch
echo "🔧 Applying ARM64 compatibility patch..."
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ -f "$SCRIPT_DIR/patches/moshi-arm64.patch" ]; then
    git apply "$SCRIPT_DIR/patches/moshi-arm64.patch"
else
    # Manual fix if patch not available
    sed -i 's/bitsandbytes >= 0.45, < 0.46/bitsandbytes >= 0.45/' pyproject.toml
fi

git add pyproject.toml
git commit -m "Fix bitsandbytes constraint for ARM64 compatibility"

# Install bitsandbytes and Moshi
echo "📦 Installing bitsandbytes and Moshi..."
source ~/kyutai-test/bin/activate
uv pip install 'bitsandbytes>=0.48'
uv pip install -e .

# Reinstall PyTorch CUDA (gets downgraded)
echo "🔥 Reinstalling PyTorch with CUDA..."
uv pip install --upgrade torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/nightly/cu130

# Verify installation
echo "🔍 Verifying Moshi installation..."
python3 -c "from moshi.models import tts; print('✓ moshi.models.tts available!')"

# Clone delayed-streams-modeling
echo "📥 Cloning delayed-streams-modeling..."
cd ~
git clone https://github.com/kyutai-labs/delayed-streams-modeling.git kyutai-dsm

# Copy API files
echo "📋 Installing API and server files..."
cp "$SCRIPT_DIR/api/kyutai_tts_api.py" ~/kyutai-dsm/
cp "$SCRIPT_DIR/api/kyutai_tts_server.py" ~/kyutai-dsm/

# Commit to git
cd ~/kyutai-dsm
git add kyutai_tts_api.py kyutai_tts_server.py
git commit -m "Add Kyutai TTS API and FastAPI server"

# Install FastAPI and uvicorn
echo "📦 Installing FastAPI and uvicorn..."
source ~/kyutai-test/bin/activate
uv pip install fastapi uvicorn

# Fix HuggingFace cache permissions
echo "🔧 Setting up HuggingFace cache..."
mkdir -p ~/.cache/huggingface/hub
sudo chown -R $USER:$USER ~/.cache/huggingface/ 2>/dev/null || true

# Install systemd service
echo "⚙️  Installing systemd service..."
sudo cp "$SCRIPT_DIR/config/kyutai-tts.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable kyutai-tts.service

# Test TTS generation
echo "🎤 Testing TTS generation..."
cd ~/kyutai-dsm
echo "Testing Kyutai TTS on ARM64" > test_input.txt
source ~/kyutai-test/bin/activate
python3 scripts/tts_pytorch.py test_input.txt test_output.wav --device cuda
echo "✓ TTS generation successful! Audio: ~/kyutai-dsm/test_output.wav"

# Start service
echo "🚀 Starting Kyutai TTS service..."
sudo systemctl start kyutai-tts.service

# Wait for startup
echo "⏳ Waiting for service to start..."
sleep 10

# Test API
echo "🔍 Testing API..."
curl -s http://localhost:8899/voices > /dev/null && echo "✓ API responding!" || echo "❌ API not responding"

echo ""
echo "======================================"
echo "✅ Installation Complete!"
echo "======================================"
echo ""
echo "Service Status:"
systemctl status kyutai-tts --no-pager
echo ""
echo "API Endpoint: http://$(hostname -I | awk '{print $1}'):8899"
echo "Logs: sudo tail -f /var/log/kyutai-tts.log"
echo ""
echo "Test with:"
echo "  curl http://localhost:8899/voices"
echo ""
