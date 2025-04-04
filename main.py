from pathlib import Path
from Components.YoutubeDownloader import download_youtube_video
from Components.Edit import extractAudio, crop_video
# from Components.Transcription import transcribeAudio
from Components.LanguageTasks import GetHighlight
from Components.FaceCrop import crop_to_vertical, combine_videos
from rehan import transcribeAudio

url = "https://www.youtube.com/watch?v=KXjEQHmWPsQ&t=9842s"
User_Input = '''Extract clips from this video where George Hotz is discussing technical topics related to computer science, programming, AI, or any relevant technical subject. Ignore sections where he goes off-topic, engages in unrelated discussions, or indulges in casual banter that does not contribute to the technical context. However, if he is reading comments and they are technical or related to the main topic, include them. Additionally, include any prerequisite explanations that provide context for deeper technical discussions. The goal is to create a streamlined version of the video that contains only valuable technical insights without unnecessary diversions.'''
print("-----------------------Downloading video and audio files-----------------------")
video_path=Path("videos/George Hotz | Programming | exploring the radeon 9070XT | AMD | tinycorp.myshopify.com.mp4")
Vid= download_youtube_video(video_fp=video_path)
if Vid:
    Vid = Vid.with_suffix(".mp4")
    print(f"Downloaded video and audio files successfully! at {Vid} ")


    Audio = extractAudio(Vid)
    print(f"------------------Extracted Audio----------------------")
    if Audio:
        print("-----------------------Transcribing Audio-----------------------")
        transcriptions = transcribeAudio(Audio)
        if len(transcriptions) > 0:
            print("-----------------------Finding Some Interesting Clip-----------------------")
            clips = GetHighlight(User_Input,transcriptions)
            # if start != 0 and stop != 0:
            #     print(f"Start: {start} , End: {stop}")

            Output = "Out.mp4"

            crop_video(Vid, Output, clips)
                # croped = "croped.mp4"
                # print("-----------------------Focusing camera on the speaker-----------------------")
                # crop_to_vertical("Out.mp4", croped)
                # combine_videos("Out.mp4", croped, "Final.mp4")
            # else:
            #     print("Error in getting highlight")
        else:
            print("No transcriptions found")
    else:
        print("No audio file found")
else:
    print("Unable to Download the video")