import ffmpeg
import threading
import queue
import time
import numpy as np
import pyaudio
import wave
import os


class AudioRecorder:
    def __init__(self, path):
        self.WAVE_OUTPUT_FILENAME = path + '.wav'
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 2
        self.RATE = 44100
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.FORMAT,
                                  channels=self.CHANNELS,
                                  rate=self.RATE,
                                  input=True,
                                  frames_per_buffer=self.CHUNK)
        self.wf = wave.open(self.WAVE_OUTPUT_FILENAME, 'wb')
        self.wf.setnchannels(self.CHANNELS)
        self.wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        self.wf.setframerate(self.RATE)
        self.recording = False
        self.thread = None

    def start(self):
        self.recording = True
        t = threading.Thread(target=self.record)
        t.start()
        self.thread = t

    def stop(self):
        self.recording = False
        self.thread.join()
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        self.wf.close()

    def record(self):
        while self.recording:
            data = self.stream.read(self.CHUNK)
            self.wf.writeframes(data)


class VideoRecorder:
    def __init__(self, input_queue: queue.Queue, path: str, radiometry: bool = True, audio: bool = True):
        self.rec_running = False
        self.thread: threading.Thread = None

        self.input_queue = input_queue
        self.path = path
        self.with_radiometry = radiometry
        self.with_audio = audio

    def capture_still(self, path: str):
        # R-JPEG?
        pass

    def rec_thread(self):
        while self.input_queue.empty():
            time.sleep(0.01)
            pass

        # TODO: silence ffmpeg outputs or log to file or sth
        # TODO: metadata

        frame = self.input_queue.queue[0]  # peek first element in queue
        rgb_resolution = frame['rgb_data'].shape
        therm_resolution = frame['thermal_data'].shape

        proc_rgb = (
            ffmpeg
            .input('pipe:', format='rawvideo', pix_fmt='rgb24', s=f'{rgb_resolution[1]}x{rgb_resolution[0]}', use_wallclock_as_timestamps='1')
            .output(self.path + '.rgb.mkv', vcodec='libx264', crf='16')
            .overwrite_output()
            .run_async(pipe_stdin=True)
        )

        if self.with_radiometry:
            proc_therm = (
                ffmpeg
                .input('pipe:', format='rawvideo', pix_fmt='gray16le', s=f'{therm_resolution[1]}x{therm_resolution[0]}', use_wallclock_as_timestamps='1')
                .output(self.path + '.therm.mkv', vcodec='ffv1')
                .overwrite_output()
                .run_async(pipe_stdin=True)
            )

        if self.with_audio:
            proc_audio = AudioRecorder(self.path)
            proc_audio.start()

        while self.rec_running:
            try:
                frame = self.input_queue.get(True, 0.1)
            except queue.Empty:
                continue

            proc_rgb.stdin.write(frame['rgb_data'].astype(np.uint8).tobytes())
            if self.with_radiometry:
                proc_therm.stdin.write(frame['thermal_data'].astype(np.uint16).tobytes())

        if self.with_audio:
            proc_audio.stop()

        proc_rgb.stdin.close()
        proc_rgb.wait()

        if self.with_radiometry:
            proc_therm.stdin.close()
            proc_therm.wait()

        # merge files
        in_streams = [ffmpeg.input(self.path + '.rgb.mkv')]
        if self.with_radiometry:
            in_streams.append(ffmpeg.input(self.path + '.therm.mkv'))
        if self.with_audio:
            in_streams.append(ffmpeg.input(self.path + '.wav'))

        out = ffmpeg.output(
            *in_streams,
            self.path + '.mkv',
            vcodec='copy',
            acodec='aac',
            map_metadata=-1,
        )
        out.run(overwrite_output=True)

        try:
            os.remove(self.path + '.rgb.mkv')
            if self.with_radiometry:
                os.remove(self.path + '.therm.mkv')
            if self.with_audio:
                os.remove(self.path + '.wav')
        except FileNotFoundError:
            pass

    def start(self):
        self.rec_running = True
        self.rec_thread = threading.Thread(target=self.rec_thread)
        self.rec_thread.start()

    def stop(self):
        self.rec_running = False
