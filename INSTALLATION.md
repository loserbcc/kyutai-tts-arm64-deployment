# Kyutai TTS Installation on ARM64 with NVIDIA CUDA

**Date**: November 2, 2025
**Platform**: NVIDIA DGX Spark (Grace Hopper ARM64 + GB10 GPU)
**Status**: FULLY OPERATIONAL ✅

## Quick Summary

Successfully deployed Kyutai/Moshi TTS with full CUDA GPU acceleration on ARM64 architecture.

## Prerequisites

- ARM64 system with NVIDIA GPU
- Ubuntu 24.04 (or similar)
- CUDA 13.0+
- Python 3.12+
- sudo access

## Installation Steps

### 1. Create Virtual Environment

```bash
python3 -m venv ~/kyutai-test
source ~/kyutai-test/bin/activate
```

### 2. Install System Dependencies

```bash
sudo apt update
sudo apt install -y libopus-dev cmake git git-lfs python3-dev
```

### 3. Install uv Package Manager

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 4. Install PyTorch with CUDA

```bash
source ~/kyutai-test/bin/activate
/home/brian/.local/bin/uv pip install torch torchvision torchaudio \
  --index-url https://download.pytorch.org/whl/nightly/cu130
```

Verify:
```bash
python3 -c "import torch; print('CUDA:', torch.cuda.is_available())"
```

### 5. Clone and Install Moshi

```bash
git clone https://github.com/kyutai-labs/moshi.git moshi-repo
cd moshi-repo/moshi

# Fix bitsandbytes constraint for ARM64
sed -i 's/bitsandbytes >= 0.45, < 0.46/bitsandbytes >= 0.45/' pyproject.toml

# Commit the fix
git config --local user.email 'your@email.com'
git config --local user.name 'Your Name'
git add pyproject.toml
git commit -m 'Fix bitsandbytes constraint for ARM64 compatibility'

# Install bitsandbytes first (ARM64 support in v0.48+)
source ~/kyutai-test/bin/activate
/home/brian/.local/bin/uv pip install 'bitsandbytes>=0.48'

# Install moshi
/home/brian/.local/bin/uv pip install -e .
```

### 6. Reinstall PyTorch CUDA

Moshi installation downgrades PyTorch to CPU version. Reinstall CUDA:

```bash
source ~/kyutai-test/bin/activate
/home/brian/.local/bin/uv pip install --upgrade torch torchvision torchaudio \
  --index-url https://download.pytorch.org/whl/nightly/cu130
```

Verify:
```bash
python3 -c "import torch; print('PyTorch:', torch.__version__); print('CUDA:', torch.cuda.is_available())"
python3 -c "from moshi.models import tts; print('moshi.models.tts available!')"
```

### 7. Clone Delayed Streams Modeling

```bash
cd ~
git clone https://github.com/kyutai-labs/delayed-streams-modeling.git kyutai-dsm
cd kyutai-dsm
```

### 8. Add API and Server Files

Copy or create `kyutai_tts_api.py` and `kyutai_tts_server.py` in the kyutai-dsm directory.

Commit:
```bash
git config --local user.email 'your@email.com'
git config --local user.name 'Your Name'
git add kyutai_tts_api.py kyutai_tts_server.py
git commit -m 'Add Kyutai TTS API and FastAPI server'
```

### 9. Install FastAPI and uvicorn

```bash
source ~/kyutai-test/bin/activate
/home/brian/.local/bin/uv pip install fastapi uvicorn
```

### 10. Fix HuggingFace Cache Permissions (if needed)

If you get permission errors:
```bash
sudo chown -R $USER:$USER ~/.cache/huggingface/
```

### 11. Test TTS Generation

```bash
cd ~/kyutai-dsm
echo "Testing Kyutai TTS on ARM64" > test_input.txt
source ~/kyutai-test/bin/activate
python3 scripts/tts_pytorch.py test_input.txt test_output.wav --device cuda
```

### 12. Create Systemd Service

Create `/etc/systemd/system/kyutai-tts.service`:

```ini
[Unit]
Description=Kyutai TTS Server (ARM64 + CUDA)
After=network.target

[Service]
Type=simple
User=brian
WorkingDirectory=/home/brian/kyutai-dsm
Environment="PATH=/home/brian/kyutai-test/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/home/brian/kyutai-test/bin/uvicorn kyutai_tts_server:app --host 0.0.0.0 --port 8899
Restart=always
RestartSec=10
StandardOutput=append:/var/log/kyutai-tts.log
StandardError=append:/var/log/kyutai-tts.log

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable kyutai-tts.service
sudo systemctl start kyutai-tts.service
systemctl status kyutai-tts.service
```

### 13. Test API

```bash
# List voices
curl http://localhost:8899/voices | jq

# Generate speech
echo '{"text": "Hello from ARM64", "voice": "happy"}' > /tmp/test.json
curl -X POST http://localhost:8899/synthesize \
  -H 'Content-Type: application/json' \
  -d @/tmp/test.json
```

## Performance

**Test Results**:
- 8.00s audio generated in 7.45s (on GB10 GPU)
- Sample rate: 24kHz, 16-bit mono WAV
- ~1.0x realtime generation speed

## Troubleshooting

### Python.h Not Found

Install python3-dev:
```bash
sudo apt install -y python3-dev
```

### Permission Denied on HuggingFace Cache

Fix ownership:
```bash
sudo chown -R $USER:$USER ~/.cache/huggingface/
```

### GPU Capability Warning

This warning is safe to ignore:
```
Found GPU0 NVIDIA GB10 which is of cuda capability 12.1.
Minimum and Maximum cuda capability supported... (8.0) - (12.0)
```

GPU acceleration works despite the warning.

## Key Changes for ARM64

1. **bitsandbytes version**: Changed from `< 0.46` to no upper limit
   - ARM64 wheels only available in v0.48+

2. **System dependencies**: `python3-dev` required for compilation

3. **PyTorch**: Use nightly builds with CUDA 13.0

## API Endpoints

**Base URL**: `http://localhost:8899`

- `GET /voices` - List available voices
- `POST /synthesize` - Generate speech
- `GET /download/{filename}` - Download generated audio

## Service Management

```bash
# Status
systemctl status kyutai-tts

# Restart
sudo systemctl restart kyutai-tts

# Logs
sudo tail -f /var/log/kyutai-tts.log
```

## Success Indicators

✅ PyTorch 2.10.0.dev with CUDA 13.0
✅ NVIDIA GB10 GPU detected
✅ moshi.models.tts available
✅ TTS generation working
✅ FastAPI server responding
✅ Systemd service enabled

---

**Installation Complete!** 🎉

The Kyutai TTS server is now running on ARM64 with full CUDA GPU acceleration.
