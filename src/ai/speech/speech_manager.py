"""Speech recognition and synthesis implementation"""

import logging
import io
import wave
from typing import Optional, Tuple
from src.config import settings

try:
    import whisper
except ImportError:
    whisper = None

try:
    from pydub import AudioSegment
    from pydub.playback import play
except ImportError:
    AudioSegment = None
    play = None

try:
    import sounddevice as sd
    import soundfile as sf
except ImportError:
    sd = None
    sf = None

try:
    from TTS.api import TTS
except ImportError:
    TTS = None

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

logger = logging.getLogger(__name__)

class SpeechManager:
    """Manages speech recognition and synthesis"""
    
    def __init__(self):
        """Initialize speech manager"""
        self.is_listening = False
        self.whisper_model = None
        self.tts_engine = None
        self.sample_rate = settings.sample_rate
        self.chunk_size = settings.chunk_size
        
        self._initialize_models()
    
    def _initialize_models(self) -> None:
        """Initialize speech models"""
        # Initialize Whisper for STT
        if whisper:
            try:
                logger.info("[Speech] Loading Whisper model...")
                self.whisper_model = whisper.load_model("base")
                logger.info("[Speech] Whisper model loaded")
            except Exception as e:
                logger.warning(f"[Speech] Failed to load Whisper: {e}")
        else:
            logger.warning("[Speech] Whisper not installed")
        
        # Initialize TTS
        if pyttsx3:
            try:
                logger.info("[Speech] Initializing pyttsx3 TTS...")
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 150)  # Speed
                self.tts_engine.setProperty('volume', 0.9)  # Volume
                logger.info("[Speech] TTS engine initialized")
            except Exception as e:
                logger.warning(f"[Speech] Failed to initialize TTS: {e}")
        else:
            logger.warning("[Speech] pyttsx3 not installed")
    
    async def recognize_speech(self, timeout: Optional[float] = None) -> Optional[str]:
        """Recognize speech from microphone using Whisper"""
        logger.info("[Speech] Recognizing speech...")
        
        if not whisper or not self.whisper_model:
            logger.error("[Speech] Whisper not available")
            return None
        
        if not sd or not sf:
            logger.error("[Speech] Audio recording not available")
            return None
        
        try:
            # Record audio
            logger.info(f"[Speech] Recording audio for {timeout or 10} seconds...")
            duration = timeout or 10
            audio = sd.rec(int(duration * self.sample_rate), samplerate=self.sample_rate, channels=1)
            sd.wait()
            
            # Save to temporary file
            temp_file = "temp_audio.wav"
            sf.write(temp_file, audio, self.sample_rate)
            
            # Transcribe with Whisper
            logger.info("[Speech] Transcribing audio...")
            result = self.whisper_model.transcribe(temp_file, language="ko")
            recognized_text = result["text"]
            
            logger.info(f"[Speech] Recognized: {recognized_text}")
            return recognized_text
        
        except Exception as e:
            logger.error(f"[Speech] Recognition failed: {e}", exc_info=True)
            return None
    
    async def synthesize_speech(self, text: str, speed: float = 1.0) -> bool:
        """Convert text to speech and play"""
        logger.info(f"[Speech] Synthesizing speech: {text}")
        
        if not self.tts_engine:
            logger.error("[Speech] TTS engine not available")
            return False
        
        try:
            self.tts_engine.setProperty('rate', int(150 * speed))
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            logger.info("[Speech] Speech synthesis completed")
            return True
        except Exception as e:
            logger.error(f"[Speech] Synthesis failed: {e}")
            return False
    
    async def detect_wake_word(self) -> bool:
        """Detect wake word in audio stream"""
        logger.debug("[Speech] Detecting wake word...")
        
        if not sd or not sf or not self.whisper_model:
            logger.error("[Speech] Audio processing not available")
            return False
        
        try:
            # Record short audio chunk
            duration = 3  # 3 second chunks
            audio = sd.rec(int(duration * self.sample_rate), samplerate=self.sample_rate, channels=1)
            sd.wait()
            
            # Save and transcribe
            temp_file = "temp_wake_word.wav"
            sf.write(temp_file, audio, self.sample_rate)
            result = self.whisper_model.transcribe(temp_file, language="ko")
            text = result["text"].lower()
            
            # Check for wake words
            wake_words = ["헤이 노바", "노바", "hey nova"]
            detected = any(word in text for word in wake_words)
            
            if detected:
                logger.info(f"[Speech] Wake word detected: {text}")
            
            return detected
        
        except Exception as e:
            logger.error(f"[Speech] Wake word detection failed: {e}")
            return False
    
    async def record_audio(self, duration: float = 5.0) -> Optional[str]:
        """Record audio from microphone"""
        logger.info(f"[Speech] Recording audio for {duration} seconds")
        
        if not sd or not sf:
            logger.error("[Speech] Audio recording not available")
            return None
        
        try:
            audio = sd.rec(int(duration * self.sample_rate), samplerate=self.sample_rate, channels=1)
            sd.wait()
            
            audio_path = "recording.wav"
            sf.write(audio_path, audio, self.sample_rate)
            logger.info(f"[Speech] Audio recorded to {audio_path}")
            return audio_path
        except Exception as e:
            logger.error(f"[Speech] Recording failed: {e}")
            return None
    
    async def play_audio(self, path: str) -> bool:
        """Play audio file"""
        logger.info(f"[Speech] Playing audio: {path}")
        
        if not AudioSegment or not play:
            logger.error("[Speech] Audio playback not available")
            return False
        
        try:
            sound = AudioSegment.from_wav(path)
            play(sound)
            logger.info("[Speech] Audio playback completed")
            return True
        except Exception as e:
            logger.error(f"[Speech] Playback failed: {e}")
            return False
