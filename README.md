# Kyutai TTS for ARM64 with NVIDIA CUDA

Production-ready deployment of Kyutai/Moshi TTS on ARM64 systems with NVIDIA GPUs.

## Quick Start

### One-Command Installation

```bash
./install.sh
```

That's it! The script will:
- Install all system dependencies
- Set up Python environment with CUDA
- Clone and patch Moshi for ARM64
- Install FastAPI server
- Create systemd service
- Test the installation

### Manual Installation

See [INSTALLATION.md](INSTALLATION.md) for step-by-step guide.

## Requirements

- ARM64 system (aarch64)
- NVIDIA GPU with CUDA support
- Ubuntu 24.04 or similar
- sudo access

**Tested On**:
- NVIDIA DGX Spark (Grace Hopper GB10)

## Performance

- Generation Speed: ~1.0-1.1x realtime
- Quality: 24kHz 16-bit mono WAV
- Voices: 8 emotions (happy, sad, calm, angry, confused, fearful, sleepy, neutral)

## Usage

### API Endpoints

```bash
# List voices
curl http://localhost:8899/voices

# Generate speech
curl -X POST http://localhost:8899/synthesize \
  -H 'Content-Type: application/json' \
  -d '{"text": "Hello world", "voice": "happy"}'
```

### Service Management

```bash
sudo systemctl status kyutai-tts    # Check status
sudo systemctl restart kyutai-tts   # Restart
sudo tail -f /var/log/kyutai-tts.log # View logs
```

## Documentation

- [Installation Guide](INSTALLATION.md) - Detailed setup instructions
- [Management Guide](docs/MANAGEMENT.md) - Daily operations
- [Technical Details](docs/TECHNICAL.md) - Architecture and implementation

## Deploy to Multiple Sparks

```bash
# Copy to new Spark
scp -r kyutai-tts-arm64-deployment new-spark:~/

# SSH and install
ssh new-spark
cd ~/kyutai-tts-arm64-deployment
./install.sh
```

## What Makes This Special

This may be the **first successful deployment of Kyutai/Moshi TTS on ARM64 with NVIDIA CUDA**.

Key achievements:
- ✅ PyTorch with CUDA on ARM64
- ✅ bitsandbytes ARM64 compatibility fix
- ✅ Automated deployment script
- ✅ Production-ready systemd service
- ✅ Full API server with FastAPI

## Architecture

- **Platform**: ARM64 (aarch64)
- **GPU**: NVIDIA CUDA 13.0+
- **Framework**: PyTorch 2.10.0.dev with CUDA
- **Model**: Kyutai Moshi TTS 1.6B
- **Server**: FastAPI + uvicorn
- **Deployment**: systemd service

## Contributing

Found this useful? Consider:
- Star this repo
- Share with others deploying on ARM64
- Report issues or improvements

## Credits

- Kyutai Labs for Moshi/Kyutai TTS
- Built for LoserBuddy distributed AI system
- Deployed on NVIDIA DGX Spark fleet

## License

Follows upstream Kyutai/Moshi licensing (MIT/Apache 2.0)

---

**Deployment Date**: November 2, 2025
**Status**: Production Ready ✅
