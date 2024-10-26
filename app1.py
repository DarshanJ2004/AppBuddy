import pandas as pd
from pydub import AudioSegment
import whisper
from groq import Groq
import os

# Initialize with your API key
client = Groq(api_key="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")

# Global variable to store flagged timestamps
flagged_timestamps = []

def transcribe_audio_whisper(file_path):
    model = whisper.load_model("base")  # Load a model
    result = model.transcribe(file_path)  # Transcribe the audio file
    return result['text']

def generate_detailed_summary(text, chunk_size=600):
    sentences = text.split('. ')  # Split on sentences for better chunking
    chunks = []
    current_chunk = []

    for sentence in sentences:
        current_chunk.append(sentence)
        # If the current chunk exceeds the chunk size, finalize it
        if sum(len(s) for s in current_chunk) > chunk_size:
            chunks.append('. '.join(current_chunk))
            current_chunk = []

    # Add any remaining sentences as a final chunk
    if current_chunk:
        chunks.append('. '.join(current_chunk))

    detailed_summaries = []
    
    for chunk in chunks:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Please provide a detailed summary of the following text: '{chunk}'. "
                        "Make sure to include key points and main ideas, and also include useful links and some graphs or tabular data. "
                        "Also explain in basic terms and if possible, use analogies."
                    ),
                }
            ],
            model="llama3-8b-8192",
        )
        detailed_summaries.append(chat_completion.choices[0].message.content)

    # Combine the detailed summaries of all chunks
    combined_summary = " ".join(detailed_summaries)
    
    return combined_summary

def extract_subclips_from_csv(audio_file_path, csv_file_path):
    # Load the CSV file
    df = pd.read_csv(csv_file_path)

    # Load the audio file
    audio = AudioSegment.from_file(audio_file_path)

    # Loop through each timestamp in the dataframe
    for index, row in df.iterrows():
        # Assuming the timestamp column is named 'timestamp' and is in seconds
        timestamp = row['timestamp']
        
        # Calculate the start and end times in milliseconds
        start_time = (timestamp - 1) * 1000  # 1 second before the timestamp
        end_time = (timestamp + 1) * 1000    # 1 second after the timestamp
        
        # Extract the subclip
        subclip = audio[start_time:end_time]
        
        # Export the subclip to a file
        output_file_path = f'subclip_{index}.mp3'  # Naming convention for output files
        subclip.export(output_file_path, format='mp3')
        print(f'Exported subclip {index}: {output_file_path}')

def save_flagged_timestamps_to_csv(csv_file_path):
    """Save the flagged timestamps to a CSV file."""
    os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)  # Ensure the directory exists
    df = pd.DataFrame(flagged_timestamps, columns=["timestamp"])
    df.to_csv(csv_file_path, index=False)
    print(f"Flagged timestamps saved to: {csv_file_path}")

def flag_timestamp(current_time):
    """Flag a timestamp during recording and add it to the list."""
    global flagged_timestamps
    flagged_timestamps.append(current_time)
    print(f"Flagged timestamp: {current_time}")

def process_audio_file(audio_file_path, csv_file_path):
    transcription = transcribe_audio_whisper(audio_file_path)
    summary = generate_detailed_summary(transcription)
    
    # Save flagged timestamps to CSV if there are any
    if flagged_timestamps:
        save_flagged_timestamps_to_csv(csv_file_path)
        extract_subclips_from_csv(audio_file_path, csv_file_path)  # Call to extract subclips
    
    return transcription, summary

# Example usage
if __name__ == "__main__":
    audio_file_path = "/Users/darshanjethva/Desktop/mumbaihacks/project1/uploads"  # Replace with your audio file path
    csv_file_path = "/Users/darshanjethva/Desktop/mumbaihacks/project1¸"  # Replace with desired CSV path
    # Flag some timestamps for demonstration
    flag_timestamp(10)  # Example: Flagging timestamp at 10 seconds
    flag_timestamp(20)  # Example: Flagging timestamp at 20 seconds
    transcription, summary = process_audio_file(audio_file_path, csv_file_path)
    print("Transcription:", transcription)
    print("Summary:", summary)
