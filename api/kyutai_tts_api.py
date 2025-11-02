#!/usr/bin/env python3
"""
Kyutai TTS API - Clean interface for MCP integration
"""
import os
import tempfile
import torch
import numpy as np
import sphn
from typing import Optional, Dict, List
from pathlib import Path
from moshi.models.loaders import CheckpointInfo
from moshi.models.tts import DEFAULT_DSM_TTS_REPO, DEFAULT_DSM_TTS_VOICE_REPO, TTSModel


class KyutaiTTS:
    """Clean API wrapper for Kyutai TTS system"""
    
    def __init__(self, device: str = "cuda", repo: str = DEFAULT_DSM_TTS_REPO):
        """Initialize the TTS model"""
        self.device = torch.device(device)
        self.repo = repo
        self.model = None
        self.sample_rate = None
        
    def load_model(self):
        """Lazy load the model on first use"""
        if self.model is None:
            print("Loading Kyutai TTS model...")
            checkpoint_info = CheckpointInfo.from_hf_repo(self.repo)
            self.model = TTSModel.from_checkpoint_info(
                checkpoint_info, 
                n_q=32, 
                temp=0.6, 
                device=self.device
            )
            self.sample_rate = self.model.mimi.sample_rate
            print("Model loaded successfully!")
    
    def list_voices(self) -> List[Dict[str, str]]:
        """List available voices"""
        # These are the main expressive voices available
        voices = [
            {"id": "happy", "path": "expresso/ex03-ex01_happy_001_channel1_334s.wav", "emotion": "happy"},
            {"id": "sad", "path": "expresso/ex03-ex02_sad-sympathetic_001_channel1_454s.wav", "emotion": "sad"},
            {"id": "confused", "path": "expresso/ex03-ex01_confused_001_channel1_909s.wav", "emotion": "confused"},
            {"id": "default", "path": "expresso/ex03-ex01_happy_001_channel1_334s.wav", "emotion": "neutral"},
            # Emotional voices using our downloaded embeddings
            {"id": "angry", "path": "expresso/ex03-ex01_angry_001_channel1_201s.wav", "emotion": "angry"},
            {"id": "calm", "path": "expresso/ex03-ex01_calm_001_channel1_1143s.wav", "emotion": "calm"},
            {"id": "fearful", "path": "expresso/ex04-ex02_fearful_001_channel1_316s.wav", "emotion": "fearful"},
            {"id": "sleepy", "path": "expresso/ex03-ex01_sleepy_001_channel1_619s.wav", "emotion": "sleepy"},
        ]
        return voices
    
    def synthesize(self, 
                   text: str, 
                   voice: str = "default",
                   output_path: Optional[str] = None,
                   return_audio: bool = False) -> Dict:
        """
        Synthesize speech from text
        
        Args:
            text: Text to synthesize
            voice: Voice ID or path (default, happy, sad, confused, or full path)
            output_path: Optional path to save audio file
            return_audio: If True, return audio data in response
            
        Returns:
            Dict with synthesis results
        """
        self.load_model()
        
        # Map voice shortcuts to full paths
        voice_map = {v["id"]: v["path"] for v in self.list_voices()}
        if voice in voice_map:
            voice_path = voice_map[voice]
        else:
            voice_path = voice
            
        # Prepare text for synthesis
        entries = self.model.prepare_script([text], padding_between=1)
        
        # Get voice embedding
        voice_embedding_path = self.model.get_voice_path(voice_path)
        condition_attributes = self.model.make_condition_attributes(
            [voice_embedding_path], cfg_coef=2.0
        )
        
        # Generate audio
        result = self.model.generate([entries], [condition_attributes])
        
        # Decode audio
        with self.model.mimi.streaming(1), torch.no_grad():
            pcms = []
            for frame in result.frames[self.model.delay_steps :]:
                pcm = self.model.mimi.decode(frame[:, 1:, :]).cpu().numpy()
                pcms.append(np.clip(pcm[0, 0], -1, 1))
            audio_data = np.concatenate(pcms, axis=-1)
        
        # Calculate duration
        duration = len(audio_data) / self.sample_rate
        
        # Save to file if requested
        if output_path:
            sphn.write_wav(output_path, audio_data, self.sample_rate)
            
        # Prepare response
        response = {
            "success": True,
            "duration": duration,
            "sample_rate": self.sample_rate,
            "voice": voice,
            "text_length": len(text),
            "output_path": output_path
        }
        
        if return_audio:
            response["audio_data"] = audio_data.tolist()
            
        return response
    
    def synthesize_batch(self, texts: List[str], voice: str = "default") -> List[Dict]:
        """Synthesize multiple texts efficiently"""
        results = []
        for text in texts:
            result = self.synthesize(text, voice=voice)
            results.append(result)
        return results


# Convenience functions for direct use
_tts_instance = None

def get_tts_instance():
    """Get or create singleton TTS instance"""
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = KyutaiTTS()
    return _tts_instance

def synthesize(text: str, voice: str = "default", output_path: Optional[str] = None) -> Dict:
    """Simple synthesis function"""
    tts = get_tts_instance()
    return tts.synthesize(text, voice=voice, output_path=output_path)

def list_voices() -> List[Dict[str, str]]:
    """List available voices"""
    tts = get_tts_instance()
    return tts.list_voices()


# CLI interface
if __name__ == "__main__":
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Kyutai TTS API")
    parser.add_argument("command", choices=["synthesize", "list-voices", "info"])
    parser.add_argument("--text", "-t", help="Text to synthesize")
    parser.add_argument("--voice", "-v", default="default", help="Voice to use")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    if args.command == "list-voices":
        voices = list_voices()
        if args.json:
            print(json.dumps(voices, indent=2))
        else:
            for v in voices:
                print(f"{v['id']:10s} - {v['emotion']:10s} ({v['path']})")
                
    elif args.command == "synthesize":
        if not args.text:
            parser.error("--text is required for synthesize command")
        result = synthesize(args.text, voice=args.voice, output_path=args.output)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"✓ Synthesized {result['duration']:.2f}s of audio")
            if result['output_path']:
                print(f"  Saved to: {result['output_path']}")
                
    elif args.command == "info":
        info = {
            "model": DEFAULT_DSM_TTS_REPO,
            "voices": DEFAULT_DSM_TTS_VOICE_REPO,
            "device": "cuda" if torch.cuda.is_available() else "cpu",
            "sample_rate": 24000,
            "format": "16-bit PCM WAV"
        }
        if args.json:
            print(json.dumps(info, indent=2))
        else:
            for k, v in info.items():
                print(f"{k}: {v}")