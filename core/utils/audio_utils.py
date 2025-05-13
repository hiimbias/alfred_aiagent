import io
import wave
from loguru import logger
from typing import Literal
import magic
import struct

AudioFormat = Literal["wav", "webm", "mp3", "ogg", "flac", "aac", "aiff", "mpeg", "mpga", "m4a", "pcm"]

class AudioUtility:
    @staticmethod
    def detect_audio_format(audio_bytes: bytes) -> AudioFormat:
        """
        Detect the format of audio data based on file signatures.
        
        :param audio_bytes: Raw audio data bytes
        :return: String indicating the detected format
        """
        try:
            mime = magic.Magic(mime=True)
            mime_type = mime.from_buffer(audio_bytes)

            # MIME type to format mapping
            mime_to_format: dict[str, AudioFormat] = {
                "audio/wav": "wav",
                "audio/x-wav": "wav",
                "audio/webm": "webm",
                "audio/mpeg": "mp3",
                "audio/mp3": "mp3",
                "audio/ogg": "ogg",
                "audio/x-flac": "flac",
                "audio/flac": "flac",
                "audio/aac": "aac",
                "audio/x-aiff": "aiff",
                "audio/mpeg": "mpeg",
                "audio/mpa": "mpga",
                "audio/mp4": "m4a",
                "audio/L16": "pcm",  
            }

            return mime_to_format.get(mime_type, "unknown")

        except Exception as e:
            print(f"[ERROR] Failed to detect format: {e}")
            return "unknown"
    
    @staticmethod
    def validate_wav(wav_bytes: bytes) -> bool:
        """
        Validate if the given BytesIO object contains a valid WAV file.
        """
        try:
            with io.BytesIO(wav_bytes) as wav_file:
                with wave.open(wav_file, 'rb') as wf:
                    num_channels = wf.getnchannels()
                    sample_width = wf.getsampwidth()
                    frame_rate = wf.getframerate()
                    num_frames = wf.getnframes()

                    logger.info(f"Valid WAV File: {num_channels} channels, {sample_width*8}-bit, {frame_rate}Hz, {num_frames} frames")
                    return True
        except wave.Error as e:
            logger.error(f"Invalid WAV File: {e}")
            return False
    
    @staticmethod
    def raw_bytes_to_wav(raw_audio_bytes, 
                         sample_rate=16000,  # Whisper prefers 16kHz
                         num_channels=1,     # Mono is better for speech recognition
                         sample_width=2) -> io.BytesIO:  # 16-bit audio
        """
        Convert raw PCM audio bytes into a WAV file-like object.
        
        :param raw_audio_bytes: Raw PCM audio data (bytes)
        :param sample_rate: Sample rate in Hz
        :param num_channels: Number of audio channels (1=mono, 2=stereo)
        :param sample_width: Sample width in bytes (2 for 16-bit audio)
        :return: A BytesIO object containing the WAV file
        """
        # Log the size of incoming data
        logger.info(f"Converting {len(raw_audio_bytes)} bytes of raw audio data to WAV")
        
        # Check if input might already be a WAV file
        if len(raw_audio_bytes) > 44 and raw_audio_bytes.startswith(b'RIFF') and b'WAVE' in raw_audio_bytes[:12]:
            logger.info("Input appears to be already in WAV format, returning as is")
            return io.BytesIO(raw_audio_bytes)
            
        # Create a new WAV file in memory
        wav_file = io.BytesIO()
        
        try:
            with wave.open(wav_file, 'wb') as wf:
                wf.setnchannels(num_channels)      # Mono for speech recognition
                wf.setsampwidth(sample_width)      # 2 bytes = 16-bit PCM
                wf.setframerate(sample_rate)       # 16kHz for Whisper
                wf.writeframes(raw_audio_bytes)    # Write raw PCM audio data

            wav_file.seek(0)  # Move back to start for reading
            
            # Verify the WAV file is valid
            wav_file_copy = io.BytesIO(wav_file.getvalue())
            with wave.open(wav_file_copy, 'rb') as wf:
                logger.info(f"Created WAV: {wf.getnchannels()} channels, {wf.getsampwidth()*8}-bit, {wf.getframerate()}Hz, {wf.getnframes()} frames")
            
            return wav_file
        except Exception as e:
            logger.error(f"Error creating WAV file: {e}")
            # Return an empty WAV file with correct headers
            empty_wav = io.BytesIO()
            with wave.open(empty_wav, 'wb') as wf:
                wf.setnchannels(num_channels)
                wf.setsampwidth(sample_width)
                wf.setframerate(sample_rate)
                wf.writeframes(b'')  # Empty audio
            empty_wav.seek(0)
            return empty_wav
            
    @staticmethod
    def convert_audio_format(audio_bytes: bytes, source_format: str, target_format: str = "wav") -> bytes:
        """
        Convert audio from one format to another using FFmpeg.
        
        :param audio_bytes: Input audio data in bytes
        :param source_format: Source format (e.g., 'webm', 'mp3')
        :param target_format: Target format (e.g., 'wav', 'mp3')
        :return: Converted audio data in bytes
        """
        try:
            import tempfile
            import subprocess
            import os
            
            # Create temp files for input and output
            with tempfile.NamedTemporaryFile(suffix=f'.{source_format}', delete=False) as in_file:
                in_file.write(audio_bytes)
                in_path = in_file.name
                
            out_path = in_path.replace(f'.{source_format}', f'.{target_format}')
            
            # Run FFmpeg conversion
            logger.info(f"Converting {source_format} to {target_format} using FFmpeg")
            command = [
                'ffmpeg',
                '-y',  # Overwrite output files
                '-i', in_path,  # Input file
                '-ar', '16000',  # Output sample rate (16kHz for Whisper)
                '-ac', '1',      # Mono audio
                '-c:a', 'pcm_s16le' if target_format == 'wav' else 'libmp3lame',  # Codec
                out_path  # Output file
            ]
            
            # Execute ffmpeg and capture output
            process = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            if process.returncode != 0:
                logger.error(f"FFmpeg error: {process.stderr.decode()}")
                return None
                
            # Read the converted file
            with open(out_path, 'rb') as out_file:
                converted_data = out_file.read()
                
            # Clean up temp files
            os.unlink(in_path)
            os.unlink(out_path)
            
            logger.info(f"Successfully converted {len(audio_bytes)} bytes from {source_format} to {len(converted_data)} bytes of {target_format}")
            return converted_data
            
        except Exception as e:
            logger.error(f"Error converting audio format: {e}")
            return None