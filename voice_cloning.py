"""
AI Voice Cloning Module for Indian English TTS
Uses Coqui TTS for high-quality, trainable voice synthesis
"""
import os
import streamlit as st
from pathlib import Path


class IndianEnglishTTS:
    """
    Indian English Text-to-Speech with voice cloning capability
    Uses Coqui TTS (formerly Mozilla TTS) - open source, trainable
    """
    
    def __init__(self, voice_samples_dir='voice_samples'):
        """
        Initialize TTS engine
        
        Args:
            voice_samples_dir: Directory containing your voice samples for cloning
        """
        self.voice_samples_dir = voice_samples_dir
        self.tts = None
        self.model_loaded = False
        
    def setup_tts_engine(self, use_pretrained=True):
        """
        Setup TTS engine with Indian English support
        
        Args:
            use_pretrained: If True, use pretrained model; if False, use custom trained model
        """
        try:
            from TTS.api import TTS
            
            if use_pretrained:
                # Use pretrained multi-speaker English model
                # You can later fine-tune this with your voice
                model_name = "tts_models/en/ljspeech/tacotron2-DDC"
                
                # Alternative Indian English models (if available):
                # model_name = "tts_models/en/vctk/vits"  # Multi-speaker
                
                self.tts = TTS(model_name=model_name, progress_bar=False, gpu=False)
                self.model_loaded = True
                return True, "✅ Pretrained TTS model loaded"
            else:
                # Load custom trained model (after you've trained it with your voice)
                custom_model_path = os.path.join(self.voice_samples_dir, 'custom_model')
                if os.path.exists(custom_model_path):
                    self.tts = TTS(model_path=custom_model_path, config_path=f"{custom_model_path}/config.json")
                    self.model_loaded = True
                    return True, "✅ Custom voice model loaded"
                else:
                    return False, "❌ Custom model not found. Please train first."
                    
        except ImportError:
            return False, "❌ TTS library not installed. Run: pip install TTS"
        except Exception as e:
            return False, f"❌ TTS setup failed: {str(e)}"
    
    def generate_speech(self, text, output_path, speed=1.0):
        """
        Generate speech from text
        
        Args:
            text: Script to convert to speech
            output_path: Where to save the audio file
            speed: Speech speed multiplier (1.0 = normal, 0.8 = slower, 1.2 = faster)
        
        Returns:
            (success: bool, message: str)
        """
        if not self.model_loaded:
            return False, "❌ TTS model not loaded. Call setup_tts_engine() first."
        
        try:
            # Generate speech
            self.tts.tts_to_file(
                text=text,
                file_path=output_path,
                speed=speed
            )
            
            # Verify file was created
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                duration = self._get_audio_duration(output_path)
                return True, f"✅ Audio generated: {duration:.1f}s ({file_size/1024:.1f}KB)"
            else:
                return False, "❌ Audio file not created"
                
        except Exception as e:
            return False, f"❌ Speech generation failed: {str(e)}"
    
    def train_custom_voice(self, voice_samples_paths, output_model_dir, epochs=1000):
        """
        Train custom voice model using your voice samples
        
        Args:
            voice_samples_paths: List of paths to your voice recordings
            output_model_dir: Where to save the trained model
            epochs: Number of training epochs (more = better but slower)
        
        Returns:
            (success: bool, message: str)
        
        NOTE: This is a simplified training process. For production:
        1. Record 50-100 high-quality voice samples
        2. Each sample should be 3-10 seconds
        3. Use diverse sentences covering different phonemes
        4. Record in quiet environment
        5. Use consistent microphone and speaking style
        """
        try:
            # This would require actual training setup
            # For production, you'd use TTS.trainer module
            return False, "⚠️ Custom training requires manual setup. See documentation."
            
        except Exception as e:
            return False, f"❌ Training failed: {str(e)}"
    
    def _get_audio_duration(self, audio_path):
        """Get duration of audio file in seconds"""
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(audio_path)
            return len(audio) / 1000.0
        except:
            return 0.0


class SimpleTTS:
    """
    Simple fallback TTS using gTTS (Google Text-to-Speech)
    Lighter weight but less customizable
    """
    
    def __init__(self, lang='en', tld='co.in'):
        """
        Initialize simple TTS
        
        Args:
            lang: Language code (en for English)
            tld: Top-level domain for accent (co.in for Indian English)
        """
        self.lang = lang
        self.tld = tld
    
    def generate_speech(self, text, output_path, slow=False):
        """
        Generate speech using Google TTS
        
        Args:
            text: Text to convert
            output_path: Output file path
            slow: If True, speak slowly
        """
        try:
            from gtts import gTTS
            
            tts = gTTS(text=text, lang=self.lang, tld=self.tld, slow=slow)
            tts.save(output_path)
            
            if os.path.exists(output_path):
                return True, "✅ Audio generated with gTTS"
            else:
                return False, "❌ Audio file not created"
                
        except ImportError:
            return False, "❌ gTTS not installed. Run: pip install gTTS"
        except Exception as e:
            return False, f"❌ Speech generation failed: {str(e)}"


def render_voice_cloning_ui(region):
    """
    Streamlit UI for voice cloning and TTS generation
    Integrate this into your Phase 3 or Phase 4
    """
    st.markdown("#### 🎙️ AI Voice Generation")
    
    # Choose TTS engine
    tts_engine = st.radio(
        "Choose TTS Engine:",
        ["Advanced (Coqui TTS - Trainable)", "Simple (Google TTS - Indian Accent)"],
        key=f'tts_engine_{region}'
    )
    
    if "Advanced" in tts_engine:
        st.info("💡 **Coqui TTS** - Can be trained with your voice for authentic sound")
        
        # Check if custom model exists
        has_custom_model = os.path.exists('voice_samples/custom_model')
        
        col1, col2 = st.columns(2)
        
        with col1:
            if has_custom_model:
                st.success("✅ Custom voice model found")
                use_custom = st.checkbox("Use my custom voice", value=True, key=f'use_custom_{region}')
            else:
                st.warning("⚠️ No custom voice model. Using pretrained model.")
                use_custom = False
                
                # Training option
                with st.expander("🎤 Train Custom Voice Model"):
                    st.markdown("""
                    **To train your voice:**
                    1. Record 50-100 voice samples (3-10s each)
                    2. Save them in `voice_samples/` folder
                    3. Use diverse sentences
                    4. Click 'Train Model' below
                    
                    **Note:** Training takes 30-60 minutes on CPU
                    """)
                    
                    if st.button("🚀 Start Training", key=f'train_{region}'):
                        st.warning("Training feature requires manual setup. See documentation.")
        
        with col2:
            speed = st.slider("Speech Speed:", 0.7, 1.3, 1.0, 0.1, key=f'speed_{region}')
        
        # Generate button
        if f'script_full_{region}' in st.session_state:
            if st.button("🎤 Generate AI Voice", type="primary", use_container_width=True, key=f'gen_voice_{region}'):
                with st.spinner("🎙️ Generating voice..."):
                    tts = IndianEnglishTTS()
                    
                    # Setup TTS
                    success, msg = tts.setup_tts_engine(use_pretrained=not use_custom)
                    
                    if success:
                        # Generate speech
                        script = st.session_state[f'script_full_{region}']
                        output_path = f"images/voiceover_{region.lower()}_ai.mp3"
                        
                        success, msg = tts.generate_speech(script, output_path, speed=speed)
                        
                        if success:
                            st.success(msg)
                            st.audio(output_path)
                            st.session_state[f'audio_uploaded_{region}'] = True
                        else:
                            st.error(msg)
                    else:
                        st.error(msg)
        else:
            st.warning("⚠️ No script available. Complete Phase 3 first.")
    
    else:
        # Simple Google TTS
        st.info("💡 **Google TTS** - Quick and easy, Indian accent")
        
        col1, col2 = st.columns(2)
        
        with col1:
            slow_speech = st.checkbox("Speak slowly", value=False, key=f'slow_{region}')
        
        # Generate button
        if f'script_full_{region}' in st.session_state:
            if st.button("🎤 Generate Voice (Google)", type="primary", use_container_width=True, key=f'gen_voice_gtts_{region}'):
                with st.spinner("🎙️ Generating voice..."):
                    tts = SimpleTTS(lang='en', tld='co.in')  # Indian English
                    
                    script = st.session_state[f'script_full_{region}']
                    output_path = f"images/voiceover_{region.lower()}_ai.mp3"
                    
                    success, msg = tts.generate_speech(script, output_path, slow=slow_speech)
                    
                    if success:
                        st.success(msg)
                        st.audio(output_path)
                        st.session_state[f'audio_uploaded_{region}'] = True
                    else:
                        st.error(msg)
        else:
            st.warning("⚠️ No script available. Complete Phase 3 first.")


# HOW TO INTEGRATE INTO YOUR PHASE 4:
"""
In your render_phase4_assets() function, after the script display,
add a new tab or section:

tab_record, tab_upload, tab_ai = st.tabs(["🎤 Record Now", "📁 Upload File", "🤖 AI Voice"])

with tab_ai:
    render_voice_cloning_ui(region)
    
This gives users 3 options:
1. Record their own voice
2. Upload pre-recorded audio
3. Generate AI voice (with optional custom training)
"""