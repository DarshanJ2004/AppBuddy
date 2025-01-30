from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'  # Directory to save uploaded files
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed audio files darshan 
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'flac'}

def allowed_file(filename):
    """Check if the uploaded file is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    audio_file = request.files['audio']
    
    if audio_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(audio_file.filename):
        return jsonify({'error': 'Unsupported file type. Please upload an audio file.'}), 400
    
    try:
        # Save the audio file
        filename = audio_file.filename
        audio_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        audio_file.save(audio_file_path)
        
        # Process the audio file and get transcription and summary
        transcription, summary = process_audio_file(audio_file_path)
        
        return jsonify({
            'filename': filename,
            'transcription': transcription,
            'summary': summary
        })

    except Exception as e:
        # Log the exception and return an error message
        print(f"Error saving file: {e}")  # Print to console for debugging
        return jsonify({'error': 'Failed to save the audio file.'}), 500

@app.route('/flag', methods=['POST'])
def flag_timestamp():
    # Handle flagging timestamps
    data = request.json
    filename = data.get('filename')
    timestamp = data.get('timestamp')

    if not filename or not timestamp:
        return jsonify({'error': 'Filename and timestamp are required.'}), 400

    # Here you would typically save the flagged timestamp to a database or file
    # For now, we will just print it to the console
    print(f'Flagged Timestamp: {timestamp} for {filename}')
    
    return jsonify({'status': 'success', 'message': f'Flagged {timestamp} for {filename}'})

def process_audio_file(audio_file_path):
    # Call the function to transcribe the audio and generate summary
    from app1 import transcribe_audio_whisper, generate_detailed_summary

    transcription = transcribe_audio_whisper(audio_file_path)
    summary = generate_detailed_summary(transcription)
    
    return transcription, summary

if __name__ == '__main__':
    # Create the uploads folder if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    app.run(debug=True)  # Run the app in debug mode
