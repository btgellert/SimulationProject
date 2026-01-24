from pygame import mixer
import wave
import numpy as np

class Sounds:
    def __init__(self, output_file="collision_sounds.wav", sample_rate=44100):
        mixer.init(frequency=sample_rate, size=-16, channels=2, buffer=512)
        
        # Set volume to 0 to prevent any playback
        mixer.music.set_volume(0.0)

        self.sound_files = [
            "assets/meow.wav",
            "assets/rizz_sound_effect.wav"
        ]
        
        self.loop_sound_files = [
            "assets/Untitled.wav",
            "assets/Untitled (1).wav"
        ]
        
        # Pre-load audio data from WAV files
        self.sound_data = []
        for sound_file in self.sound_files:
            try:
                with wave.open(sound_file, 'rb') as wav:
                    n_frames = wav.getnframes()
                    frames = wav.readframes(n_frames)
                    # Convert to numpy array
                    audio_array = np.frombuffer(frames, dtype=np.int16)
                    file_sample_rate = wav.getframerate()
                    channels = wav.getnchannels()
                    print(f"Loaded {sound_file}: {n_frames} frames, {file_sample_rate}Hz, {channels} channels, {len(audio_array)} samples")
                    self.sound_data.append((audio_array, file_sample_rate, channels, sound_file))
            except Exception as e:
                print(f"Error loading {sound_file}: {e}")
                # Create silent audio as fallback
                self.sound_data.append((np.zeros(sample_rate * 2, dtype=np.int16), sample_rate, 2, sound_file))
        
        self.i = 0
        
        self.loop_sound_data = []
        for sound_file in self.loop_sound_files:
            try:
                with wave.open(sound_file, 'rb') as wav:
                    n_frames = wav.getnframes()
                    frames = wav.readframes(n_frames)
                    # Convert to numpy array
                    audio_array = np.frombuffer(frames, dtype=np.int16)
                    file_sample_rate = wav.getframerate()
                    channels = wav.getnchannels()
                    print(f"Loaded {sound_file}: {n_frames} frames, {file_sample_rate}Hz, {channels} channels, {len(audio_array)} samples")
                    self.loop_sound_data.append((audio_array, file_sample_rate, channels))
            except Exception as e:
                print(f"Error loading {sound_file}: {e}")
                # Create silent audio as fallback
                self.loop_sound_data.append((np.zeros(sample_rate * 2, dtype=np.int16), sample_rate, 2))
        
        
        # Recording setup
        self.output_file = output_file
        self.sample_rate = sample_rate
        self.recorded_events = []  # List of (time_offset, audio_data, sample_rate, channels) tuples
        
    def play(self, current_time=None, sound_effect=None):
        if not self.sound_data:
            print("Warning: No sound data loaded")
            return
        
        sound_to_play = None
        if sound_effect:
            self.sound_data
            sound_to_play = [s for s in self.sound_data if sound_effect in s[3]][0]
        else:
            sound_to_play = self.loop_sound_data[self.i]
            
        # Get the sound data to record
        audio_array, file_sample_rate, channels, *_ = sound_to_play
        sound_index = self.i
        self.i += 1
        if self.i >= len(self.sound_data):
            self.i = 0
        
        # Store the event with timing information
        if current_time is None:
            # If no time provided, use the length of previous events as offset
            current_time = 0.0
            for time_offset, data, sr, ch in self.recorded_events:
                duration = len(data) / (sr * ch)
                current_time = max(current_time, time_offset + duration)
        
        print(f"Recording sound event {sound_index} at time {current_time:.3f}s ({len(audio_array)} samples, {file_sample_rate}Hz, {channels}ch)")
        self.recorded_events.append((current_time, audio_array, file_sample_rate, channels))
    
    def save_recording(self, duration_seconds=None):
        if not self.recorded_events:
            print("No sound events to save")
            # Create a silent file anyway
            with wave.open(self.output_file, 'wb') as wav_file:
                wav_file.setnchannels(2)
                wav_file.setsampwidth(2)
                wav_file.setframerate(self.sample_rate)
                silent = np.zeros(int(duration_seconds or 1.0) * self.sample_rate * 2, dtype=np.int16)
                wav_file.writeframes(silent.tobytes())
            return
        
        print(f"Saving {len(self.recorded_events)} sound events...")
        
        if duration_seconds is None:
            max_time = 0.0
            for event_time, audio_data, sample_rate, channels in self.recorded_events:
                duration = len(audio_data) / (sample_rate * channels)
                max_time = max(max_time, event_time + duration)
            duration_seconds = max_time
        
        total_samples = int(duration_seconds * self.sample_rate * 2)
        mixed_audio = np.zeros(total_samples, dtype=np.int32)

        for event_idx, (event_time, audio_data, file_sample_rate, channels) in enumerate(self.recorded_events):
            # Calculate start position in output samples (stereo = 2 samples per frame)
            start_sample = int(event_time * self.sample_rate * 2)
            
            if start_sample < 0:
                print(f"  WARNING: Event {event_idx} at time {event_time:.3f}s starts before 0 (sample {start_sample})")
                continue
            if start_sample >= total_samples:
                print(f"  WARNING: Event {event_idx} at time {event_time:.3f}s starts after end (sample {start_sample} >= {total_samples})")
                continue
            
            if channels == 1:
                audio_data = np.repeat(audio_data, 2)
                channels = 2
            elif channels == 2:
                # Already stereo
                pass
            elif channels > 2:
                # Take first 2 channels
                num_samples = len(audio_data) // channels
                reshaped = audio_data[:num_samples * channels].reshape(num_samples, channels)
                stereo = reshaped[:, :2].flatten()  # Take first 2 channels and flatten back to interleaved
                audio_data = stereo
                channels = 2
            
            if file_sample_rate != self.sample_rate:
                # Resample
                ratio = self.sample_rate / file_sample_rate
                num_samples = len(audio_data) // 2  # Number of stereo pairs
                new_num_samples = int(num_samples * ratio)
                
                # Resample left and right channels separately
                left_channel = audio_data[0::2]
                right_channel = audio_data[1::2]
                
                # Resample each channel
                indices = np.linspace(0, num_samples - 1, new_num_samples)
                left_resampled = np.interp(indices, np.arange(num_samples), left_channel.astype(np.float32)).astype(np.int16)
                right_resampled = np.interp(indices, np.arange(num_samples), right_channel.astype(np.float32)).astype(np.int16)
                
                # Interleave back: [L0, R0, L1, R1, ...]
                audio_data = np.empty(new_num_samples * 2, dtype=np.int16)
                audio_data[0::2] = left_resampled
                audio_data[1::2] = right_resampled
            
            end_sample = start_sample + len(audio_data)
            
            if end_sample > total_samples:
                max_length = total_samples - start_sample
                if max_length > 0:
                    audio_data = audio_data[:max_length]
                    end_sample = total_samples
                else:
                    print(f"  WARNING: Event {event_idx} at time {event_time:.3f}s is completely outside duration ({duration_seconds:.2f}s)")
                    continue
            
            if start_sample >= 0 and start_sample < total_samples and len(audio_data) > 0:
                # Mix
                mixed_audio[start_sample:end_sample] += audio_data.astype(np.int32)
                print(f"  Placed event {event_idx} at sample {start_sample} to {end_sample} (time {event_time:.3f}s)")
            else:
                print(f"  WARNING: Event {event_idx} at time {event_time:.3f}s could not be placed (start_sample={start_sample}, total_samples={total_samples})")
        
        mixed_audio = np.clip(mixed_audio, -32768, 32767).astype(np.int16)
        
        non_zero_samples = np.count_nonzero(mixed_audio)
        max_amplitude = np.max(np.abs(mixed_audio))
        print(f"Mixed audio: {non_zero_samples} non-zero samples out of {len(mixed_audio)}, max amplitude: {max_amplitude}")
        
        if non_zero_samples == 0:
            print("WARNING: Mixed audio contains only zeros! No sound will be audible.")
            print("Debug info:")
            for i, (event_time, audio_data, file_sample_rate, channels) in enumerate(self.recorded_events):
                non_zero = np.count_nonzero(audio_data)
                max_amp = np.max(np.abs(audio_data)) if len(audio_data) > 0 else 0
                print(f"  Event {i}: time={event_time:.3f}s, {len(audio_data)} samples, {non_zero} non-zero, max_amp={max_amp}")
        
        # Save to WAV file
        with wave.open(self.output_file, 'wb') as wav_file:
            wav_file.setnchannels(2)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(mixed_audio.tobytes())
        
        print(f"Saved {len(self.recorded_events)} sound events to {self.output_file} ({duration_seconds:.2f}s duration)")
    
    def reset(self):
        self.recorded_events = []
        self.start_time = None


sounds = Sounds()
