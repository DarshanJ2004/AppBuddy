class AudioRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.mediaStream = null;
        this.filename = 'lecture.wav';
        this.startTime = null;
        this.isUploading = false;
        
        this.initializeUI();
    }

    showError(message) {
        const errorElement = document.getElementById('errorMessage');
        errorElement.textContent = message;
        errorElement.style.display = 'block';
        setTimeout(() => {
            errorElement.style.display = 'none';
        }, 5000);
    }

    showSuccess(message) {
        const successElement = document.getElementById('successMessage');
        successElement.textContent = message;
        successElement.style.display = 'block';
        setTimeout(() => {
            successElement.style.display = 'none';
        }, 5000);
    }

    initializeUI() {
        document.getElementById('recordButton').onclick = () => this.startRecording();
        document.getElementById('stopButton').onclick = () => this.stopRecording();
        document.getElementById('flagButton').onclick = () => this.flagTimestamp();
        
        document.getElementById('stopButton').style.display = 'none';
        document.getElementById('flagButton').style.display = 'none';
    }

    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaStream = stream;
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];
            this.startTime = Date.now();

            this.mediaRecorder.addEventListener('dataavailable', event => {
                this.audioChunks.push(event.data);
            });

            this.mediaRecorder.addEventListener('stop', () => {
                this.handleRecordingComplete();
            });

            this.mediaRecorder.start();
            this.updateUIForRecording(true);
            document.getElementById('recordingIndicator').classList.add('recording');
            document.getElementById('statusText').textContent = 'Recording...';
            this.showSuccess('Recording started successfully');
        } catch (error) {
            console.error('Error starting recording:', error);
            this.showError('Failed to start recording. Please check your microphone permissions.');
        }
    }

    async handleRecordingComplete() {
        if (this.isUploading) return;
        this.isUploading = true;

        try {
            document.getElementById('statusText').textContent = 'Uploading...';
            
            const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
            const formData = new FormData();
            formData.append('audio', audioBlob, this.filename);

            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Upload failed');
            }

            const data = await response.json();
            this.filename = data.filename;

            // Update UI with transcription and summary
            this.updateTranscriptionUI(data.transcription, data.summary);
            
            this.showSuccess('Recording uploaded successfully');
            this.setupAudioPlayer();
            
            document.getElementById('recordingIndicator').classList.remove('recording');
            document.getElementById('statusText').textContent = 'Recording complete';
        } catch (error) {
            console.error('Error uploading recording:', error);
            this.showError('Failed to save recording. Please try again.');
        } finally {
            this.isUploading = false;
        }
    }

    updateTranscriptionUI(transcription, summary) {
        const transcriptionElement = document.getElementById('transcription');
        transcriptionElement.innerHTML = `<strong>Transcription:</strong> ${transcription}<br><strong>Summary:</strong> ${summary}`;
    }

    setupAudioPlayer() {
        const audioPlayer = document.getElementById('audioPlayer');
        audioPlayer.src = `/uploads/${this.filename}`;
        audioPlayer.style.display = 'block';
    }

    stopRecording() {
        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            this.mediaRecorder.stop();
            this.mediaStream.getTracks().forEach(track => track.stop());
            this.updateUIForRecording(false);
        }
    }

    async flagTimestamp() {
        try {
            const currentTime = Date.now();
            const elapsedTime = (currentTime - this.startTime) / 1000;

            const response = await fetch('/flag', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    filename: this.filename,
                    timestamp: elapsedTime
                })
            });

            if (!response.ok) {
                throw new Error('Failed to save flag');
            }

            this.showSuccess(`Flag saved at: ${elapsedTime.toFixed(2)} seconds`);
            this.updateFlaggedTimestamps(elapsedTime);
        } catch (error) {
            console.error('Error flagging timestamp:', error);
            this.showError('Failed to save flag. Please try again.');
        }
    }

    updateFlaggedTimestamps(timestamp) {
        const list = document.getElementById('flaggedTimestampsList');
        const listItem = document.createElement('li');
        listItem.textContent = `Flagged at: ${timestamp.toFixed(2)} seconds`;
        list.appendChild(listItem);
    }

    updateUIForRecording(isRecording) {
        document.getElementById('recordButton').style.display = isRecording ? 'none' : 'inline';
        document.getElementById('stopButton').style.display = isRecording ? 'inline' : 'none';
        document.getElementById('flagButton').style.display = isRecording ? 'inline' : 'none';
        document.getElementById('flagButton').disabled = !isRecording; // Disable the flag button if not recording
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const audioRecorder = new AudioRecorder();
});
