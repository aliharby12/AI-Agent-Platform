import React, { useState, useRef } from 'react';

interface MessageInputProps {
  sessionId: number | null;
  onSend: (content: string) => void;
  onSendVoice?: (audioBlob: Blob) => void;
  disabled?: boolean;
}

const MessageInput: React.FC<MessageInputProps> = ({ sessionId, onSend, onSendVoice, disabled }) => {
  const [value, setValue] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const recordingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const handleSend = () => {
    if (value.trim() && sessionId) {
      onSend(value);
      setValue('');
    }
  };

  const startRecording = async () => {
    if (!sessionId || disabled) return;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        if (onSendVoice && audioBlob.size > 0) {
          onSendVoice(audioBlob);
        }
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);

      // Start recording timer
      recordingIntervalRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);

    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Unable to access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setRecordingTime(0);
      
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
        recordingIntervalRef.current = null;
      }
    }
  };

  const handleMouseDown = () => {
    if (!isRecording) {
      startRecording();
    }
  };

  const handleMouseUp = () => {
    if (isRecording) {
      stopRecording();
    }
  };

  const handleTouchStart = (e: React.TouchEvent) => {
    e.preventDefault();
    if (!isRecording) {
      startRecording();
    }
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    e.preventDefault();
    if (isRecording) {
      stopRecording();
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const buttonStyle = {
    border: 'none',
    borderRadius: 4,
    padding: '8px 16px',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    userSelect: 'none' as const,
    touchAction: 'none' as const,
  };

  const sendButtonStyle = {
    ...buttonStyle,
    background: '#2d2dff',
    color: '#fff',
  };

  const recordButtonStyle = {
    ...buttonStyle,
    background: isRecording ? '#ff4444' : '#4caf50',
    color: '#fff',
  };

  const disabledButtonStyle = {
    ...buttonStyle,
    background: '#ccc',
    color: '#666',
    cursor: 'not-allowed',
  };

  return (
    <div className="chat-input-row">
      <input
        type="text"
        value={value}
        onChange={e => setValue(e.target.value)}
        placeholder={sessionId ? 'Type your message or use voice...' : 'Select a session to chat...'}
        style={{ flex: 1, borderRadius: 4, border: '1px solid #ccc', padding: 12 }}
        disabled={!sessionId || disabled}
        onKeyDown={e => { if (e.key === 'Enter') handleSend(); }}
      />
      <button
        style={disabled ? disabledButtonStyle : sendButtonStyle}
        disabled={!sessionId || disabled}
        onClick={handleSend}
        onMouseEnter={(e) => {
          if (!disabled && sessionId) {
            e.currentTarget.style.background = '#1a1aff';
            e.currentTarget.style.transform = 'scale(1.02)';
          }
        }}
        onMouseLeave={(e) => {
          if (!disabled && sessionId) {
            e.currentTarget.style.background = '#2d2dff';
            e.currentTarget.style.transform = 'scale(1)';
          }
        }}
      >
        Send
      </button>
      <button 
        style={disabled ? disabledButtonStyle : recordButtonStyle}
        disabled={!sessionId || disabled}
        onMouseDown={handleMouseDown}
        onMouseUp={handleMouseUp}
        onTouchStart={handleTouchStart}
        onTouchEnd={handleTouchEnd}
        onMouseEnter={(e) => {
          if (!disabled && sessionId) {
            e.currentTarget.style.background = isRecording ? '#ff6666' : '#45a049';
            e.currentTarget.style.transform = 'scale(1.02)';
          }
        }}
        onMouseLeave={(e) => {
          if (!disabled && sessionId) {
            e.currentTarget.style.background = isRecording ? '#ff4444' : '#4caf50';
            e.currentTarget.style.transform = 'scale(1)';
          }
          // Also stop recording if mouse leaves while recording
          if (isRecording) {
            stopRecording();
          }
        }}
      >
        {isRecording ? `Recording (${formatTime(recordingTime)})` : 'Hold to Talk'}
      </button>
    </div>
  );
};

export default MessageInput; 