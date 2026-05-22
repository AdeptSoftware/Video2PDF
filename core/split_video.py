# split_video.py
import core.parallel
import cv2


def run(video: cv2.VideoCapture, delay, pos, x1, x2, y1, y2, rotate):
    def iterator():
        fps      = int(video.get(cv2.CAP_PROP_FPS))
        interval = int(fps * delay / 1000.0)
        position = pos
        index    = 0

        while True:
            ret, frame = video.read()
            if not ret:
                break

            if position % interval == 0:
                yield frame, index
                index += 1
            position += 1

    def callback(data):
        frame, index = data
        frame = frame[y1:y2, x1:x2]
        if rotate:
            frame = cv2.rotate(frame, rotate)

        filename = self._output_frames.joinpath(f"{index:04d}.png")
        cv2.imwrite(filename, frame)

    total = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    core.parallel.run(callback, iterator(), total=total, desc1="Прогресс:", desc2="")