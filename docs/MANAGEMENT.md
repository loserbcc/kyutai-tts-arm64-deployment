# Kyutai TTS on Elack - Management Guide

**Quick Reference for Daily Operations**

---

## Quick Commands

### Check if Service is Running
```bash
ssh elack
systemctl status kyutai-tts
```

### Restart Service
```bash
ssh elack
sudo systemctl restart kyutai-tts
```

### View Recent Logs
```bash
ssh elack
sudo tail -50 /var/log/kyutai-tts.log
```

### Test if API is Responding
```bash
curl http://192.168.4.132:8899/voices | jq
```

---

## File Locations Cheat Sheet

### On Elack (192.168.4.132)
```
/home/brian/kyutai-test/              # Virtual environment
/home/brian/moshi-repo/               # Moshi source code
/home/brian/kyutai-dsm/               # API server location
/etc/systemd/system/kyutai-tts.service # Service file
/var/log/kyutai-tts.log               # Server logs
```

### On Moya (Local)
```
/home/brian/ELACK_KYUTAI_DEPLOYMENT_COMPLETE.md  # Full deployment doc
/home/brian/ELACK_KYUTAI_MANAGEMENT_GUIDE.md     # This guide
/home/brian/PORTS.md                              # Port registry (8899)
/home/brian/loserbuddy-mcp-servers/kyutai-emotional/index.js  # MCP integration
```

---

## Daily Operations

### Starting/Stopping Service

**Start**:
```bash
ssh elack
sudo systemctl start kyutai-tts
```

**Stop**:
```bash
ssh elack
sudo systemctl stop kyutai-tts
```

**Restart** (after changes):
```bash
ssh elack
sudo systemctl restart kyutai-tts
```

**Status Check**:
```bash
ssh elack
systemctl status kyutai-tts
# Look for: "Active: active (running)"
```

### Viewing Logs

**Live tail** (watch in real-time):
```bash
ssh elack
sudo tail -f /var/log/kyutai-tts.log
```

**Last 50 lines**:
```bash
ssh elack
sudo tail -50 /var/log/kyutai-tts.log
```

**Search for errors**:
```bash
ssh elack
sudo grep -i error /var/log/kyutai-tts.log | tail -20
```

### Testing API

**Quick health check**:
```bash
curl http://192.168.4.132:8899/voices
# Should return JSON list of voices
```

**Generate test audio**:
```bash
cat > /tmp/test.json << 'EOF'
{
  "text": "Testing Kyutai TTS",
  "voice": "happy"
}
EOF

curl -X POST http://192.168.4.132:8899/synthesize \
  -H 'Content-Type: application/json' \
  -d @/tmp/test.json
```

---

## Common Tasks

### Check GPU Status
```bash
ssh elack
nvidia-smi
# Look for: GPU utilization and memory usage
```

### Check Disk Space
```bash
ssh elack
df -h /home
# Make sure there's space for model cache
```

### Check HuggingFace Cache Size
```bash
ssh elack
du -sh ~/.cache/huggingface/
```

### Verify CUDA is Working
```bash
ssh elack
source ~/kyutai-test/bin/activate
python3 -c "import torch; print('CUDA:', torch.cuda.is_available())"
# Should print: CUDA: True
```

---

## After Elack Reboots

### Auto-Start Verification
The service should auto-start. Verify:
```bash
ssh elack
systemctl status kyutai-tts
```

If not running:
```bash
sudo systemctl start kyutai-tts
```

### Check Logs After Reboot
```bash
ssh elack
sudo journalctl -u kyutai-tts -n 50
```

---

## Troubleshooting Guide

### Service Won't Start

1. **Check logs**:
```bash
sudo journalctl -u kyutai-tts -n 100
```

2. **Verify files exist**:
```bash
ls -la /home/brian/kyutai-dsm/kyutai_tts_server.py
ls -la /home/brian/kyutai-test/bin/uvicorn
```

3. **Test manually**:
```bash
cd /home/brian/kyutai-dsm
source ~/kyutai-test/bin/activate
uvicorn kyutai_tts_server:app --host 0.0.0.0 --port 8899
# Press Ctrl+C to stop, then restart service
```

### API Not Responding

1. **Check if service is running**:
```bash
systemctl status kyutai-tts
```

2. **Check if port is listening**:
```bash
ss -tlnp | grep 8899
```

3. **Check firewall** (if applicable):
```bash
sudo ufw status
```

4. **Test locally on Elack**:
```bash
ssh elack
curl http://localhost:8899/voices
```

### CUDA Errors

1. **Check GPU**:
```bash
nvidia-smi
```

2. **Verify PyTorch CUDA**:
```bash
source ~/kyutai-test/bin/activate
python3 -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
```

3. **Reinstall if needed**:
```bash
source ~/kyutai-test/bin/activate
/home/brian/.local/bin/uv pip install --upgrade torch \
  --index-url https://download.pytorch.org/whl/nightly/cu130
```

### Permission Errors

**HuggingFace cache**:
```bash
sudo chown -R brian:brian ~/.cache/huggingface/
```

**Log file**:
```bash
sudo chown brian:brian /var/log/kyutai-tts.log
```

---

## Updating the Service

### Update API Code

1. **Make changes to files**:
```bash
ssh elack
cd ~/kyutai-dsm
nano kyutai_tts_server.py  # or kyutai_tts_api.py
```

2. **Commit to git**:
```bash
git add .
git commit -m "Description of changes"
```

3. **Restart service**:
```bash
sudo systemctl restart kyutai-tts
```

4. **Check logs**:
```bash
sudo tail -30 /var/log/kyutai-tts.log
```

### Update Moshi/PyTorch

**Not recommended unless necessary** - requires full reinstallation.

If needed, follow: `/home/brian/kyutai-dsm/INSTALLATION_ARM64.md`

---

## Monitoring

### Check Service Health
```bash
# Create a simple health check script
cat > ~/check_kyutai.sh << 'EOF'
#!/bin/bash
echo "Checking Kyutai TTS Service..."
ssh elack "systemctl status kyutai-tts | grep Active"
curl -s http://192.168.4.132:8899/voices > /dev/null && echo "✓ API responding" || echo "✗ API not responding"
EOF
chmod +x ~/check_kyutai.sh

# Run it
~/check_kyutai.sh
```

### Check GPU Usage
```bash
ssh elack
watch -n 1 nvidia-smi  # Updates every second
```

### Check Memory Usage
```bash
ssh elack
free -h
```

---

## Integration with MCP Servers

### Current Setup
The `kyutai-emotional` MCP server automatically uses Elack as primary backend.

**File**: `/home/brian/loserbuddy-mcp-servers/kyutai-emotional/index.js`

**Failover Order**:
1. Try Elack (192.168.4.132:8899) first
2. Fall back to Moya (localhost:8899) if Elack unavailable

### Testing MCP Integration
Your MCP servers will automatically use Elack when generating emotion voices.
No manual intervention needed - it just works!

---

## Backup & Recovery

### Important Files to Backup
```bash
# On Elack
/home/brian/kyutai-dsm/kyutai_tts_api.py
/home/brian/kyutai-dsm/kyutai_tts_server.py
/etc/systemd/system/kyutai-tts.service

# Git repos (already have commits)
/home/brian/moshi-repo/
/home/brian/kyutai-dsm/
```

### Quick Backup
```bash
# From Moya
ssh elack "cd ~/kyutai-dsm && git log --oneline -5"
ssh elack "cd ~/moshi-repo && git log --oneline -5"

# All changes are committed to git!
```

### Recovery After Fresh Install
If Elack is rebuilt, follow:
`/home/brian/kyutai-dsm/INSTALLATION_ARM64.md`

All steps documented with exact commands.

---

## Performance Expectations

### Normal Operation
- **Generation Speed**: ~1.0-1.1x realtime
- **Memory Usage**: ~800MB when idle, ~4-6GB during generation
- **GPU Usage**: Spikes during generation, idle otherwise
- **Response Time**: 5-10 seconds for typical sentences

### When to Worry
- API not responding after 30 seconds
- CUDA errors in logs
- Service keeps restarting
- Generation takes >2x realtime

---

## Contact & Documentation

### Full Documentation
- **Complete Guide**: `/home/brian/ELACK_KYUTAI_DEPLOYMENT_COMPLETE.md`
- **This Guide**: `/home/brian/ELACK_KYUTAI_MANAGEMENT_GUIDE.md`
- **Installation Steps**: `/home/brian/kyutai-dsm/INSTALLATION_ARM64.md` (on Elack)
- **Port Registry**: `/home/brian/PORTS.md`

### Quick Links
- Kyutai/Moshi GitHub: https://github.com/kyutai-labs/moshi
- Delayed Streams Modeling: https://github.com/kyutai-labs/delayed-streams-modeling

---

## Emergency Procedures

### Service is Down and Won't Start

1. **Check basic status**:
```bash
ssh elack
systemctl status kyutai-tts
sudo journalctl -u kyutai-tts -n 50
```

2. **Try manual start**:
```bash
cd /home/brian/kyutai-dsm
source ~/kyutai-test/bin/activate
python3 -m uvicorn kyutai_tts_server:app --host 0.0.0.0 --port 8899
# Watch for errors
```

3. **Check dependencies**:
```bash
source ~/kyutai-test/bin/activate
python3 -c "import torch, moshi, fastapi; print('All imports OK')"
```

4. **Last resort** - Reinstall (takes ~30 minutes):
Follow `/home/brian/kyutai-dsm/INSTALLATION_ARM64.md`

### Elack Was Rebooted/Reset

If all files are gone (like what happened today), reinstall:
```bash
# Follow full installation guide
/home/brian/kyutai-dsm/INSTALLATION_ARM64.md
# Or from Moya:
/home/brian/ELACK_KYUTAI_DEPLOYMENT_COMPLETE.md
```

All steps documented with exact commands used.

---

## Summary

**Most Common Commands**:
```bash
# Check status
ssh elack; systemctl status kyutai-tts

# Restart
ssh elack; sudo systemctl restart kyutai-tts

# View logs
ssh elack; sudo tail -50 /var/log/kyutai-tts.log

# Test API
curl http://192.168.4.132:8899/voices
```

**Service Location**: Elack (192.168.4.132:8899)
**Auto-starts**: Yes
**Logs**: `/var/log/kyutai-tts.log`
**Integration**: Automatic via MCP servers

---

**Questions?** Check `/home/brian/ELACK_KYUTAI_DEPLOYMENT_COMPLETE.md` for full details.
