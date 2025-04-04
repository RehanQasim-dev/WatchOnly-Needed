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
    # print(json_string)
    for i, line in enumerate(json_string.split("\n")):
        print(i, " ", line)
    # json_string = json_string.replace('```json', '').replace('```', '').strip()
    if not json_string.strip().endswith(']}'):
        json_string=json_string[:json_string.rindex('}')+1]+']}'  # Ensure valid JSON format
    for i, line in enumerate(json_string.split("\n")):
        print(i, " ", line)
    clips = json.loads(json_string)  # Parse JSON
    return clips['timestamps']
# Function to get highlights using Gemini Chat API
def GetHighlight(user_input, trans_clips):
    print("Getting Highlights from Transcription...")
    model = "gemini-2.0-flash"
    config = types.GenerateContentConfig(
        temperature=0.6,
        top_p=0.8,
        system_instruction=system_instruction,
        response_mime_type="application/json",
       response_schema=genai.types.Schema(
            type = genai.types.Type.OBJECT,
            required = ["timestamps"],
            properties = {
                "timestamps": genai.types.Schema(
                    type = genai.types.Type.ARRAY,
                    items = genai.types.Schema(
                        type = genai.types.Type.OBJECT,
                        required = ["start", "end"],
                        properties = {
                            "start": genai.types.Schema(
                                type = genai.types.Type.NUMBER,
                            ),
                            "end": genai.types.Schema(
                                type = genai.types.Type.NUMBER,
                            ),
                        },
                    ),
                ),
            },
        ),
    )
    # Convert trans_clips to a string for input
    transcription = "\n".join([f"{start} - {end}: {text}" for text, start, end in trans_clips])
    
    # Start a chat session
    initial_prompt = f"{user_input}\n\ntranscript:\n{transcription}"
    response = client.models.generate_content(
        model=model,
        config=config,
        contents=[initial_prompt],
    )
    
    # Initial message
   
    # print(initial_prompt)
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
    # {"timestamps": [{"start": 9502.262, "end": 9509.889}]}
    while not json_string.strip().endswith(']}'):  # Likely truncated
        print("Response truncated, continuing...")
        last_end = all_clips[-1]["end"] if all_clips else "0.0"  # Last clip’s end time
        prompt=f"Continue extracting clips starting from sentence ending at time {last_end} to the end. these are the instructions {user_input} \n\ntranscript:\n{transcription}"
        response = client.models.generate_content(
        model=model,
        config=config,
        contents=[prompt],
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
    
    user_input = '''You are an AI assistant tasked with extracting clips from a transcript of a George Hotz stream to create a streamlined version focused on technical content. Return a valid JSON in this format: [{"start": "Start time", "end": "End Time", "title": "Clip title"}]. Each clip must be continuous, combining multiple sentences if needed. "Start" is the start_timestamp of the first sentence, "end" is the ending timestamp of the last sentence, and "title" is a concise description of the clip’s technical content (e.g., "AI Discussion", "Coding Neural Network"). Clips should be ordered by timestamp, with earlier clips appearing first.

Extract clips where George Hotz discusses technical topics related to computer science, programming, AI, or any relevant technical subject. Include:
- Direct technical discussions (e.g., coding explanations, algorithms, AI concepts).
- Prerequisite explanations or transitions that set up deeper technical discussions, even if they seem casual, as long as they connect to the main topic within 15 seconds.
- Segments where he reads viewer comments, but only if they are technical (e.g., about programming, AI, or the current topic) and contribute to the discussion.
- Short silences (< 30 seconds) immediately following technical content, as these may represent coding or thinking time related to the topic. Assign these a title like "Coding Pause" unless context suggests otherwise.

Exclude:
- Off-topic banter, casual tangents, or unrelated discussions (e.g., food, personal anecdotes) unless they provide immediate context for technical content.
- Segments where he reads casual or unrelated comments (e.g., "What’s your favorite pizza?").
- Long silences (> 2 minutes), which likely indicate breaks (e.g., bathroom, stepping away), unless preceded by technical content and followed by its continuation.
- Any silence or speech not tied to the technical focus of the stream.

Additional Guidelines:
- Favor longer, continuous clips over fragmented ones when the content remains relevant or transitions smoothly. If two relevant segments are separated by less than 20 seconds of irrelevant content or silence, merge them into one clip with an appropriate title (e.g., "Algorithm Setup and Implementation").
- For silences tagged as "[silence]" in the transcript, evaluate their context: include short silences after technical talk as potential coding/thinking time, but exclude long silences unless they bridge related technical segments.
- If a silence occurs mid-discussion and the topic resumes afterward, consider including it as part of the clip if it’s short (< 30 seconds) and relevant.

The goal is to capture all valuable technical insights—including verbal explanations, comment interactions, and silent coding/thinking moments—while removing unnecessary diversions for a focused viewing experience. Process the transcript provided below and return the JSON output.'''
    
    print(f"Transcript length: {len(trans_text)} characters")
    clips = GetHighlight(user_input, trans_clips)
    # print("Extracted clips:", json.dumps(clips, indent=2))

# 3.25 hours -> 135200 characters -> 67,000 tokens (max input tokens 1000,000)

# (1000,000*3.25/67,000)= 48.5 hours of george hotz video
# {"start": "5241.391", "end": "5243.292"}-> 25 tokens
#  8192/25 = 327.68 clips