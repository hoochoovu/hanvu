import os
import shutil
import tempfile
from moviepy.editor import VideoFileClip
import nemo.collections.asr as nemo_asr
import librosa
import soundfile as sf

def create_temp_folder():
    """Create a temporary folder for audio files."""
    return tempfile.mkdtemp()

def extract_audio(file_path, temp_folder):
    """Extract audio from video if needed and ensure mono format."""
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    if file_path.lower().endswith(('.mp4', '.mkv', '.avi', '.mov')):
        clip = VideoFileClip(file_path)
        audio_path = os.path.join(temp_folder, f"{base_name}.wav")
        clip.audio.write_audiofile(audio_path)
    elif file_path.lower().endswith(('.mp3', '.wav', '.flac', '.aac', '.ogg')):
        audio_path = file_path
    else:
        raise ValueError("Unsupported file type.")
    
    # Load the audio file and convert to mono if necessary
    audio, sr = librosa.load(audio_path, sr=None, mono=False)
    if audio.ndim > 1:
        audio = librosa.to_mono(audio)
    
    # Save as mono WAV file
    mono_audio_path = os.path.join(temp_folder, f"{base_name}_mono.wav")
    sf.write(mono_audio_path, audio, sr)
    
    return mono_audio_path

      
def generate_subtitles(asr_model, audio_path, txt_output_path):
    """Generate subtitles using NVIDIA NeMo ASR model with proper timestamping."""
    # Transcribe the audio file
    transcript = asr_model.transcribe([audio_path])[0]
    
    # Get audio duration
    audio_duration = librosa.get_duration(filename=audio_path)
    
    # Split transcript into words
    words = transcript.split()
    
    # Estimate time per word (assuming uniform distribution)
    time_per_word = audio_duration / len(words)
    
    with open(txt_output_path, 'w') as f:
        current_time = 0
        word_count = 0
        line = []
        for i, word in enumerate(words):
            line.append(word)
            word_count += 1
            current_time = (i + 1) * time_per_word  # Calculate time based on word index
            if word_count >= 5 or current_time >= 5:  # Write subtitle every 5 words or 5 seconds
                start_time = max(0, current_time - word_count * time_per_word)
                end_time = current_time
                f.write(f"{format_time(start_time)} --> {format_time(end_time)}\n")
                f.write(f"{' '.join(line)}\n\n")
                line = []
                word_count = 0
    

def format_time(seconds):
    """Format time in HH:MM:SS,mmm format."""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},{int((seconds % 1) * 1000):03d}"

def process_folder(asr_model, input_folder, output_folder):
    """Process all files in the input folder."""
    temp_folder = create_temp_folder()
    try:
        for root, _, files in os.walk(input_folder):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    audio_path = extract_audio(file_path, temp_folder)
                    output_path = os.path.join(output_folder, os.path.relpath(root, input_folder))
                    os.makedirs(output_path, exist_ok=True)
                    txt_output_path = os.path.join(output_path, f"{os.path.splitext(file)[0]}.txt")
                    generate_subtitles(asr_model, audio_path, txt_output_path)
                    print(f"Subtitles generated for {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    finally:
        # Clean up temporary folder
        shutil.rmtree(temp_folder)

# Load NVIDIA NeMo ASR model (conformer-based)
asr_model = nemo_asr.models.ASRModel.from_pretrained(model_name="stt_en_conformer_ctc_small")

# Replace with your input and output folder paths
input_folder = 'input'
output_folder = 'output'

# Process the input folder
process_folder(asr_model, input_folder, output_folder)