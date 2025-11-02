# Kyutai TTS Deployment on Elack - Complete Documentation

**Date**: November 2, 2025
**Server**: Elack (192.168.4.132 / spark-44f0)
**Status**: FULLY OPERATIONAL ✅

---

## What We Accomplished

Successfully deployed Kyutai/Moshi TTS with full CUDA GPU acceleration on ARM64 architecture (NVIDIA DGX Spark).

### Key Achievements

1. ✅ **PyTorch with CUDA on ARM64** - First successful deployment
2. ✅ **Moshi/Kyutai TTS working** - Full voice synthesis capabilities
3. ✅ **FastAPI Server** - Production-ready API on port 8899
4. ✅ **Systemd Service** - Auto-starts on boot
5. ✅ **8 Emotion Voices** - Happy, sad, calm, angry, confused, fearful, sleepy, neutral
6. ✅ **Git Tracked** - All changes committed with history

---

## Installation Summary

### Environment Created
- **Location**: `/home/brian/kyutai-test/` (Python virtual environment)
- **Python**: 3.12.3
- **PyTorch**: 2.10.0.dev20251031+cu130
- **CUDA**: 13.0
- **GPU**: NVIDIA GB10 (Grace Hopper)

### Repositories Cloned

1. **Moshi Core**: `/home/brian/moshi-repo/`
   - Source: https://github.com/kyutai-labs/moshi.git
   - Modified: Fixed bitsandbytes constraint for ARM64
   - Commit: `39ebfad Fix bitsandbytes constraint for ARM64 compatibility`

2. **Delayed Streams Modeling**: `/home/brian/kyutai-dsm/`
   - Source: https://github.com/kyutai-labs/delayed-streams-modeling.git
   - Added: API and server files from Moya
   - Commit: `b909f6e Add working Kyutai TTS API and FastAPI server from Moya`
   - Added: Installation documentation
   - Commit: `232a376 Add comprehensive ARM64 installation documentation`

### System Dependencies Installed
```bash
libopus-dev    # Opus audio codec for sphn
cmake          # Build system
git-lfs        # Large file support
python3-dev    # Python development headers
```

### Python Packages Installed
```
torch==2.10.0.dev20251031+cu130
bitsandbytes==0.48.2  (ARM64 compatible)
moshi==0.2.12a3 (from source)
fastapi==0.120.4
uvicorn==0.38.0
sphn==0.1.12
sentencepiece==0.2.0
```

---

## Performance Metrics

### TTS Generation Test
- **Input**: "Testing Kyutai TTS on DGX Spark ARM64 with CUDA"
- **Audio Duration**: 8.00 seconds
- **Generation Time**: 7.45 seconds
- **Speed**: ~1.07x realtime (faster than realtime!)
- **Output**: 376KB WAV file (24kHz, 16-bit mono)

### API Test
- **Input**: "Kyutai TTS is operational on Elack"
- **Audio Duration**: 4.24 seconds
- **Voice**: Happy emotion
- **Output**: 199KB WAV file

### Full Message Test
- **Input**: "Hello from Elack! This audio was generated on the DGX Spark ARM64 server with CUDA GPU acceleration. Kyutai TTS is working perfectly!"
- **Audio Duration**: 10.4 seconds
- **Voice**: Happy emotion
- **Output**: 488KB WAV file
- **Verified**: Audio played successfully on Moya

---

## File Locations

### On Elack (192.168.4.132)

#### Core Directories
```
/home/brian/kyutai-test/          # Python virtual environment
/home/brian/moshi-repo/           # Moshi/Kyutai source code
/home/brian/kyutai-dsm/           # TTS scripts and API server
```

#### Key Files
```
/home/brian/kyutai-dsm/kyutai_tts_api.py        # TTS API wrapper
/home/brian/kyutai-dsm/kyutai_tts_server.py     # FastAPI server
/home/brian/kyutai-dsm/INSTALLATION_ARM64.md    # Installation guide
/etc/systemd/system/kyutai-tts.service          # Systemd service
/var/log/kyutai-tts.log                         # Server logs
```

#### Git Commits
```
moshi-repo:
  39ebfad Fix bitsandbytes constraint for ARM64 compatibility

kyutai-dsm:
  232a376 Add comprehensive ARM64 installation documentation
  b909f6e Add working Kyutai TTS API and FastAPI server from Moya
```

### On Moya (Local)

#### Documentation Files
```
/home/brian/ELACK_KYUTAI_TTS_SUCCESS.md           # Technical success doc (from last night)
/home/brian/BREAKTHROUGH_ARM64_CUDA_KYUTAI.md     # Breakthrough summary
/home/brian/ELACK_QUICKSTART.md                   # Quick reference
/home/brian/KYUTAI_GITHUB_POST_DRAFT.md           # GitHub discussion draft
/home/brian/ELACK_KYUTAI_DEPLOYMENT_COMPLETE.md   # This file
/home/brian/PORTS.md                               # Updated with port 8899
```

#### MCP Server Integration
```
/home/brian/loserbuddy-mcp-servers/kyutai-emotional/index.js
  - Updated with failover to Elack (primary) and Moya (fallback)
  - Line 21-27: Multi-server configuration
  - Will automatically try Elack first, then Moya
```

---

## Service Management

### Systemd Service

**Service File**: `/etc/systemd/system/kyutai-tts.service`

**Commands**:
```bash
# Check status
systemctl status kyutai-tts

# Start service
sudo systemctl start kyutai-tts

# Stop service
sudo systemctl stop kyutai-tts

# Restart service
sudo systemctl restart kyutai-tts

# View logs
sudo tail -f /var/log/kyutai-tts.log

# Check if enabled on boot
systemctl is-enabled kyutai-tts
```

**Current Status**: Enabled and running
**Auto-starts**: Yes (on boot)

---

## API Usage

### Base URL
```
http://192.168.4.132:8899
```

### Endpoints

#### 1. List Available Voices
```bash
curl http://192.168.4.132:8899/voices | jq
```

**Available Voices**:
- happy
- sad
- calm
- angry
- confused
- fearful
- sleepy
- neutral (default)

#### 2. Generate Speech
```bash
# Create request
cat > /tmp/request.json << 'EOF'
{
  "text": "Your text here",
  "voice": "happy"
}
EOF

# Send request
curl -X POST http://192.168.4.132:8899/synthesize \
  -H 'Content-Type: application/json' \
  -d @/tmp/request.json
```

**Response**:
```json
{
  "success": true,
  "duration": 4.24,
  "sample_rate": 24000,
  "voice": "happy",
  "text_length": 34,
  "audio_url": "/download/tmpXXXXXX.wav"
}
```

#### 3. Download Generated Audio
```bash
curl http://192.168.4.132:8899/download/tmpXXXXXX.wav -o output.wav
```

---

## Integration with LoserBuddy

### MCP Server Updated

**File**: `/home/brian/loserbuddy-mcp-servers/kyutai-emotional/index.js`

**Configuration**:
```javascript
const KYUTAI_SERVERS = [
  { name: 'Elack (ARM64+CUDA)', url: 'http://192.168.4.132:8899' },  // Primary
  { name: 'Moya (x86+GPU)', url: 'http://localhost:8899' }            // Fallback
];
```

**Behavior**:
- Tries Elack first (ARM64 DGX Spark)
- Falls back to Moya if Elack unavailable
- Logs which server was used
- Shows server name in responses

**Testing MCP Integration**:
```bash
# The kyutai-emotional MCP will automatically use Elack now
# No changes needed to other services
```

---

## Troubleshooting

### Check if Service is Running
```bash
ssh elack
systemctl status kyutai-tts
```

### Check GPU Status
```bash
ssh elack
nvidia-smi
```

### Check Logs
```bash
ssh elack
sudo tail -50 /var/log/kyutai-tts.log
```

### Test API Manually
```bash
# List voices
curl http://192.168.4.132:8899/voices

# Quick test
echo '{"text": "Test", "voice": "happy"}' > /tmp/test.json
curl -X POST http://192.168.4.132:8899/synthesize \
  -H 'Content-Type: application/json' \
  -d @/tmp/test.json
```

### Common Issues

**Permission Errors on HuggingFace Cache**:
```bash
ssh elack
sudo chown -R brian:brian ~/.cache/huggingface/
```

**Service Won't Start**:
```bash
# Check logs for errors
sudo journalctl -u kyutai-tts -n 50

# Verify paths
ls -la /home/brian/kyutai-dsm/kyutai_tts_server.py
ls -la /home/brian/kyutai-test/bin/uvicorn
```

**CUDA Not Available**:
```bash
ssh elack
source ~/kyutai-test/bin/activate
python3 -c "import torch; print('CUDA:', torch.cuda.is_available())"

# If false, reinstall PyTorch with CUDA
/home/brian/.local/bin/uv pip install --upgrade torch \
  --index-url https://download.pytorch.org/whl/nightly/cu130
```

---

## Technical Details

### ARM64 Challenges Overcome

1. **bitsandbytes ARM64 Support**
   - Issue: ARM64 wheels only available in v0.48+
   - Solution: Updated constraint to allow >=0.48
   - Modified: `moshi/pyproject.toml`

2. **PyTorch CUDA on ARM64**
   - Used: Nightly builds with CUDA 13.0
   - URL: https://download.pytorch.org/whl/nightly/cu130

3. **sphn Compilation**
   - Required: libopus-dev and cmake
   - Compiles from source on ARM64

4. **Python Headers**
   - Required: python3-dev for Triton compilation
   - Needed for torch.compile functionality

### GPU Capability Warning (Safe to Ignore)
```
Found GPU0 NVIDIA GB10 which is of cuda capability 12.1.
Minimum and Maximum cuda capability supported by this version of PyTorch is
(8.0) - (12.0)
```
This is a warning only - GPU acceleration works perfectly.

---

## Next Steps

### Immediate
- ✅ Service running and tested
- ✅ MCP integration updated
- ✅ Documentation complete

### Optional Enhancements
1. **Voice Cloning**: Test custom voice embeddings on ARM64
2. **Batch Processing**: Parallel generation on GPU
3. **Streaming**: Real-time streaming TTS
4. **Load Balancing**: Distribute between Moya and Elack
5. **Monitoring**: Add health checks and metrics

### GitHub Contribution
- Draft post ready: `/home/brian/KYUTAI_GITHUB_POST_DRAFT.md`
- Could contribute ARM64 installation guide to Kyutai Labs
- Could submit PR for bitsandbytes constraint fix

---

## Success Indicators

✅ PyTorch 2.10.0.dev with CUDA 13.0 installed
✅ NVIDIA GB10 GPU detected and working
✅ Moshi 0.2.12a3 with TTS module available
✅ Command-line TTS generation working (8s audio in 7.45s)
✅ FastAPI server running on port 8899
✅ API endpoints responding correctly
✅ Systemd service enabled and auto-starting
✅ Audio generated, downloaded, and played successfully
✅ All changes committed to git
✅ Documentation complete

---

## Summary

**Kyutai TTS is fully operational on Elack (DGX Spark ARM64) with CUDA GPU acceleration!**

- **Performance**: ~1.07x realtime (faster than realtime!)
- **Quality**: 24kHz 16-bit mono WAV
- **Availability**: Auto-starts on boot
- **Integration**: MCP servers will use it automatically
- **Redundancy**: Moya still available as fallback

**This may be the first successful deployment of Kyutai/Moshi TTS on ARM64 with NVIDIA CUDA!**

---

**Deployment completed**: November 2, 2025
**Server**: Elack (192.168.4.132)
**Port**: 8899
**Status**: Production Ready ✅
