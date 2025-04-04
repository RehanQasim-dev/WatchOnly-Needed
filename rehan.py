import whisperx
import gc 
import torch
def transcribeAudio(audio_path):
    batch_size = 16
    compute_type = "float16"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("Transcribing audio...")
    model_dir = "/media/SSD2_Partition1/personal_work/AI-Youtube-Shorts-Generator/models"
    model = whisperx.load_model("base.en", device, compute_type=compute_type, download_root=model_dir)
    print("Model loaded")
    audio = whisperx.load_audio(audio_path)
    result = model.transcribe(audio, batch_size=batch_size)
    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
    result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)
    extracted_texts = [[segment['text'], segment['start'], segment['end']] for segment in result["segments"]]
    return extracted_texts



