import os
from pytubefix import YouTube
import ffmpeg
from pathlib import Path
def get_video_size(stream):

    return stream.filesize / (1024 * 1024)

def download_youtube_video(url=None,video_fp=None) -> Path:
    if url is None and video_fp is None:
        print("Please provide either a URL or a video file path.")
        return "error"
    if url:
        yt = YouTube(url)

        video_streams = yt.streams.filter(type="video").order_by('resolution').desc()
        audio_stream = yt.streams.filter(only_audio=True).first()

        print("Available video streams:")
        for i, stream in enumerate(video_streams):
            size = get_video_size(stream)
            stream_type = "Progressive" if stream.is_progressive else "Adaptive"
            print(f"{i}. Resolution: {stream.resolution}, Size: {size:.2f} MB, Type: {stream_type}")

        choice = int(input("Enter the number of the video stream to download: "))
        selected_stream = video_streams[choice]

        if not os.path.exists('videos'):
            os.makedirs('videos')

        print(f"Downloading video: {yt.title}")
        video_file = selected_stream.download(output_path='videos', filename_prefix="video_")

        if not selected_stream.is_progressive:
            print("Downloading audio...")
            audio_file = audio_stream.download(output_path='videos', filename_prefix="audio_")

            print("Merging video and audio...")
            output_file = os.path.join('videos', f"{yt.title}.mp4")
            stream = ffmpeg.input(video_file)
            audio = ffmpeg.input(audio_file)
            stream = ffmpeg.output(stream, audio, output_file, vcodec='libx264', acodec='aac', strict='experimental')
            ffmpeg.run(stream, overwrite_output=True)

            os.remove(video_file)
            os.remove(audio_file)
        else:
            output_file = video_file

        
        print(f"Downloaded: {yt.title} to 'videos' folder")
        print(f"File path: {output_file}")
        return Path(output_file)
    elif video_fp:  
        if not os.path.exists(video_fp):
            print(f"Video file {video_fp} does not exist.")
            return "error"

        return video_fp
if __name__ == "__main__":
    youtube_url = input("Enter YouTube video URL: ")
    download_youtube_video(youtube_url)
