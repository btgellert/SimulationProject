import pyaudiowpatch as pyaudio
import wave
import threading
import time
AUDIO_TEMP = "temp_audio.wav"

class AudioRecorder(threading.Thread):
    def __init__(self, seconds):
        super().__init__()
        self.recording = False
        self.p = pyaudio.PyAudio()
        self.seconds = seconds
        
        try:
            wasapi_info = self.p.get_host_api_info_by_type(pyaudio.paWASAPI)
            default_speakers = self.p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
            
            if not default_speakers["isLoopbackDevice"]:
                for loopback in self.p.get_loopback_device_info_generator():
                    if default_speakers["name"] in loopback["name"]:
                        default_speakers = loopback
                        break

            self.wave_file = wave.open(AUDIO_TEMP, 'wb')
            self.wave_file.setnchannels(default_speakers["maxInputChannels"])
            self.wave_file.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
            self.wave_file.setframerate(int(default_speakers["defaultSampleRate"]))

            def callback(in_data, frame_count, time_info, status):
                self.wave_file.writeframes(in_data)
                return (in_data, pyaudio.paContinue)

            self.stream = self.p.open(format=pyaudio.paInt16,
                                      channels=default_speakers["maxInputChannels"],
                                      rate=int(default_speakers["defaultSampleRate"]),
                                      input=True, input_device_index=default_speakers["index"],
                                      stream_callback=callback)
        except Exception as e:
            print(f"Audio Error: {e}")

    def run(self):
        self.recording = True
        self.stream.start_stream()
        time.sleep(self.seconds+2)
        self.stream.stop_stream()
        self.stream.close()
        self.wave_file.close()
        self.p.terminate()