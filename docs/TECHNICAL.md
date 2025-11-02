# Draft GitHub Discussion/Issue for Kyutai Labs

**Title**: ✅ Successful Deployment on ARM64 with NVIDIA CUDA (Grace Hopper)

---

## Summary

Successfully deployed Moshi TTS on **NVIDIA DGX Spark (ARM64 Grace Hopper architecture)** with full CUDA GPU acceleration! This may be the first ARM64 + CUDA deployment of Kyutai/Moshi.

## Hardware

- **Platform**: NVIDIA DGX Spark
- **CPU**: ARM64 (Grace)
- **GPU**: NVIDIA GB10 (Hopper) - CUDA Capability 12.1
- **Architecture**: Grace Hopper (unified CPU+GPU)

## Software Stack

- **OS**: Ubuntu 24.04 (ARM64)
- **Python**: 3.12.3
- **PyTorch**: 2.10.0.dev20251031+cu130
- **CUDA**: 13.0
- **Moshi**: 0.2.12a3 (installed from source)

## Changes Required

### 1. bitsandbytes Version Constraint

**Issue**: The `pyproject.toml` specifies `bitsandbytes >= 0.45, < 0.46`, but ARM64 wheels are only available in v0.48+.

**Fix**: Modified `moshi/pyproject.toml`:
```diff
- "bitsandbytes >= 0.45, < 0.46; sys_platform == 'linux'",
+ "bitsandbytes >= 0.45; sys_platform == 'linux'",
```

Then installed with: `pip install 'bitsandbytes>=0.48'`

### 2. System Dependencies

Required for `sphn` package compilation on ARM64:
```bash
sudo apt install -y libopus-dev cmake
```

### 3. PyTorch Installation

Used PyTorch nightly with CUDA 13.0:
```bash
pip install torch torchvision torchaudio \
  --index-url https://download.pytorch.org/whl/nightly/cu130
```

## Performance

**Test Generation**:
- **Input**: 67 characters of text
- **Output**: 5.44 seconds of audio
- **Generation Time**: ~6 seconds total
- **Quality**: Excellent (24kHz, 16-bit WAV)
- **Voice**: Happy (emotion voice)

~1.0x realtime generation speed with GPU acceleration.

## Installation Steps

```bash
# 1. Create virtual environment
python3 -m venv kyutai-test
source kyutai-test/bin/activate

# 2. Install system dependencies
sudo apt install -y libopus-dev cmake

# 3. Install PyTorch with CUDA
pip install torch torchvision torchaudio \
  --index-url https://download.pytorch.org/whl/nightly/cu130

# 4. Install bitsandbytes (ARM64 compatible version)
pip install 'bitsandbytes>=0.48'

# 5. Clone and install Moshi
git clone https://github.com/kyutai-labs/moshi.git
cd moshi/moshi

# 6. Fix bitsandbytes constraint in pyproject.toml
sed -i 's/bitsandbytes >= 0.45, < 0.46/bitsandbytes >= 0.45/' pyproject.toml

# 7. Install Moshi
pip install -e .

# 8. Verify installation
python3 -c "import moshi.models.tts; print('Success!')"
```

## Production Deployment

Created a FastAPI server using the delayed-streams-modeling TTS scripts. Service runs on port 8899 with systemd auto-start.

## Minor Warnings

```
Found GPU0 NVIDIA GB10 which is of cuda capability 12.1.
Minimum and Maximum cuda capability supported by this version of PyTorch is
(8.0) - (12.0)
```

This is a warning only - GPU acceleration works perfectly despite the capability mismatch.

## Why This Matters

Grace Hopper (ARM64 + NVIDIA GPU) is an emerging architecture for AI workloads. This deployment proves:
- Moshi/Kyutai is portable to ARM64 with minimal changes
- Performance is excellent on Grace Hopper
- ARM64 is viable for production TTS deployments

## Suggestions for Upstream

1. **Update bitsandbytes constraint** to allow v0.48+ for ARM64 support
2. **Document ARM64 deployment** in README
3. **Add CI testing** for ARM64 if possible
4. **Note system dependencies** (libopus-dev, cmake) for sphn compilation

## Notes on Voice System

Kyutai uses **pre-computed voice embeddings** (not real-time cloning):
- Uses emotion voices from "Expresso" dataset
- Embeddings stored in HuggingFace repo: `kyutai/tts-voices`
- Available emotions: happy, sad, calm, angry, confused, fearful, sleepy
- Works perfectly on ARM64 with these pre-computed embeddings

## Questions

- Is ARM64 support a priority for the Kyutai team?
- Would you accept a PR to update the bitsandbytes constraint?
- Any interest in ARM64-specific optimizations?
- Are there plans to support custom voice embedding generation?

Happy to provide more details or testing assistance!

---

**Environment Details**:
- Moshi repo: https://github.com/kyutai-labs/moshi
- Deployed as: Production FastAPI TTS server
- Integration: LoserBuddy distributed AI communication system
