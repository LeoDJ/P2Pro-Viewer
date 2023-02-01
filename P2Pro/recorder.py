import ffmpeg
import threading
import queue
import time
import numpy as np

class Recorder:
    rec_running = False
    rec_thread: threading.Thread

    def capture_still(self, path: str):
        # R-JPEG?
        pass

    def rec_thread(self, input_queue: queue.Queue, path: str, with_audio: bool):
        while input_queue.empty():
            time.sleep(0.01)
            pass

        # TODO: Audio
        # TODO: silence ffmpeg outputs or log to file or sth

        frame = input_queue.queue[0]  # peek first element in queue
        rgb_resolution = frame['rgb_data'].shape
        therm_resolution = frame['thermal_data'].shape

        proc_rgb = (
            ffmpeg
            .input('pipe:', format='rawvideo', pix_fmt='rgb24', s=f'{rgb_resolution[1]}x{rgb_resolution[0]}', use_wallclock_as_timestamps='1')
            .output(path + '.rgb.mkv', vcodec='libx264', crf='16')
            .overwrite_output()
            .run_async(pipe_stdin=True)
        )

        proc_therm = (
            ffmpeg
            .input('pipe:', format='rawvideo', pix_fmt='gray16le', s=f'{therm_resolution[1]}x{therm_resolution[0]}', use_wallclock_as_timestamps='1')
            .output(path + '.therm.mkv', vcodec='ffv1')
            .overwrite_output()
            .run_async(pipe_stdin=True)
        )


        while self.rec_running:
            try:
                frame = input_queue.get(True, 0.1)
            except queue.Empty:
                continue

            # Test frame drop handling
            # if frame['frame_num'] > 25 and frame['frame_num'] < 50:
            #     continue

            proc_rgb.stdin.write(frame['rgb_data'].astype(np.uint8).tobytes())
            proc_therm.stdin.write(frame['thermal_data'].astype(np.uint16).tobytes())

        proc_rgb.stdin.close()
        proc_therm.stdin.close()

        proc_rgb.wait()
        proc_therm.wait()

        in_streams = [
            ffmpeg.input(path + '.rgb.mkv'),
            ffmpeg.input(path + '.therm.mkv')
        ]
        out = ffmpeg.output(
            *in_streams,
            path + '.mkv',
            vcodec='copy',
            acodec='copy',
            map_metadata=-1,
        )
        out.run(overwrite_output=True)
        # print(out.get_args())

        # TODO: metadata
        # TODO: delete temp files


    def start_rec(self, input_queue: queue.Queue, path: str, with_audio: bool = True):
        self.rec_running = True

        self.rec_thread = threading.Thread(target=self.rec_thread, args=(input_queue, path, with_audio,))
        self.rec_thread.start()

        pass

    def stop_rec(self):
        self.rec_running = False