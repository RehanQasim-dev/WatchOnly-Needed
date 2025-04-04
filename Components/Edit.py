from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.editor import VideoFileClip,concatenate_videoclips
import subprocess
from pathlib import Path
def extractAudio(video_path):
    video_clip = VideoFileClip(str(video_path))
    audio_path = video_path.parent / f"{video_path.stem}audio.wav"
    if not audio_path.exists():
        video_clip.audio.write_audiofile(str(audio_path))
        video_clip.close()
        print(f"Extracted audio to: {audio_path}")
    return audio_path


def crop_video(input_file, output_file, clips):
    with VideoFileClip(str(input_file)) as video:
        extracted_clips = [video.subclip(clip['start'], clip['end']) for clip in clips]

        if extracted_clips:  # Ensure there is at least one clip
            final_video = concatenate_videoclips(extracted_clips)
            final_video.write_videofile(str(output_file), codec='libx264')
        else:
            print("No valid clips provided.")

# Example usage:
if __name__ == "__main__":
    input_file = r"Example.mp4" ## Test
    print(input_file)
    output_file = "Short.mp4"
    start_time = 31.92 
    end_time = 49.2   

    crop_video(input_file, output_file, start_time, end_time)

