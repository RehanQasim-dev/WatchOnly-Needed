from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import json

# Load API Key from .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("API key not found. Make sure it is defined in the .env file as GEMINI_API_KEY.")

# Initialize Gemini client
client = genai.Client(api_key=api_key)

# System instruction for Gemini API
system_instruction = (
    "You are an AI assistant that extracts clips from a transcript according to the criteria given by the user. "
    "Return a valid JSON in this format: [{\"start\": \"Start time\", \"end\": \"End Time\"}]\n\n"
    "Each clip must be continuous and could consist of multiple sentences combined together. "
    "Start is the start_timestamp of the first sentence, and end is the ending timestamp of the last sentence. "
    "All clips in the JSON should be ordered by timestamp, with clips earlier in the transcript appearing first."
)

# Function to extract start and end times from JSON response
def extract_times(json_string):
    json_string = json_string.replace('```json', '').replace('```', '').strip()
    json_string=json_string[:json_string.rindex('}')+1]+']'  # Ensure valid JSON format
    # for i, line in enumerate(json_string.split("\n")):
    #     print(i, " ", line)
    clips = json.loads(json_string)  # Parse JSON
    return clips
# Function to get highlights using Gemini Chat API
def GetHighlight(user_input, trans_clips):
    print("Getting Highlights from Transcription...")
    model = "gemini-2.0-flash"
    
    # Convert trans_clips to a string for input
    transcription = "\n".join([f"{start} - {end}: {text}" for text, start, end in trans_clips])
    
    # Start a chat session
    chat = client.chats.create(model=model,config=types.GenerateContentConfig(
            temperature=0.6,
            top_p=0.8,
            system_instruction=system_instruction))
    
    # Initial message
    initial_prompt = f"{user_input}\n\ntranscript:\n{transcription}"
    # print(initial_prompt)
    response = chat.send_message(
        initial_prompt
    )
    # for message in chat.get_history():
    #     print(f'role - {message.role}',end=": ")
    #     print(message.parts[0].text)
    all_clips = []
    json_string = response.text
    clips = extract_times(json_string)
    all_clips.extend(clips)
    
    # Check if response is truncated (near token limit or incomplete JSON)
    token_info = client.models.count_tokens(model=model, contents=[response.text])
    print("Token count:", token_info.total_tokens)
    
    while not json_string.strip().endswith('```'):  # Likely truncated
        print("Response truncated, continuing...")
        last_end = all_clips[-1]["end"] if all_clips else "0.0"  # Last clip’s end time
        response = chat.send_message(
            f"Continue extracting clips starting after the clip ending at {last_end}.",
        )
        # for message in chat.get_history():
        #     print(f'role - {message.role}',end=": ")
        #     print(message.parts[0].text)
        json_string = response.text
        clips = extract_times(json_string)
        all_clips.extend(clips)
        token_info = client.models.count_tokens(model=model, contents=[response.text])
        print("Token count:", token_info.total_tokens)
    
    return all_clips

# Run the script
if __name__ == "__main__":
    # Load transcript and convert to list of [text, start, end]
    with open("Transcription.txt", "r") as f:
        trans_text = f.read()
    
    # Assuming Transcription.txt is formatted like "start - end: text"
    trans_clips = []
    for line in trans_text.splitlines():
        if line.strip():
            time_part, text = line.split(": ", 1)
            start, end = time_part.split(" - ")
            trans_clips.append([text.strip(), float(start), float(end)])
    
    user_input = (
        "Extract clips from this video where George Hotz is discussing technical topics related to "
        "computer science, programming, AI, or any relevant technical subject. Ignore sections where "
        "he goes off-topic, engages in unrelated discussions, or indulges in casual banter that does "
        "not contribute to the technical context. However, if he is reading comments and they are "
        "technical or related to the main topic, include them. Additionally, include any prerequisite "
        "explanations that provide context for deeper technical discussions. The goal is to create a "
        "streamlined version of the video that contains only valuable technical insights without "
        "unnecessary diversions."
    )
    
    print(f"Transcript length: {len(trans_text)} characters")
    clips = GetHighlight(user_input, trans_clips)
    # print("Extracted clips:", json.dumps(clips, indent=2))

# 3.25 hours -> 135200 characters -> 67,000 tokens (max input tokens 1000,000)

# (1000,000*3.25/67,000)= 48.5 hours of george hotz video
# {"start": "5241.391", "end": "5243.292"}-> 25 tokens
#  8192/25 = 327.68 clips