"""Background capture worker; UI never blocks on camera reads or inference."""
from __future__ import annotations

import logging
from pathlib import Path
from queue import Empty, Full, Queue
from threading import Event, Thread
import time

import cv2
import numpy as np

from .vision import FaceEngine, FaceObservation

logger = logging.getLogger(__name__)


class CameraWorker:
    def __init__(self, engine: FaceEngine, source: int | str = 0):
        self.engine = engine
        self.source = source
        self.frames: Queue[tuple[np.ndarray, list[FaceObservation]]] = Queue(maxsize=1)
        self._stop = Event()
        self._thread: Thread | None = None
        self.error: str | None = None
        self.running = False

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self.error = None
        self._thread = Thread(target=self._run, name='kkb-camera', daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
        self.running = False

    def latest(self) -> tuple[np.ndarray, list[FaceObservation]] | None:
        try:
            return self.frames.get_nowait()
        except Empty:
            return None

    def _emit(self, frame: np.ndarray, detections: list[FaceObservation]) -> None:
        try:
            self.frames.put_nowait((frame, detections))
        except Full:
            try:
                self.frames.get_nowait()
            except Empty:
                pass
            self.frames.put_nowait((frame, detections))

    def _run(self) -> None:
        source = self.source
        if isinstance(source, str) and Path(source).is_file():
            frame = cv2.imread(source)
            if frame is None:
                self.error = 'Impossible de lire la photo de démonstration.'
                return
            try:
                self._emit(frame, self.engine.process(frame))
            except Exception as exc:
                self.error = str(exc)
            return

        camera = cv2.VideoCapture(source)
        if not camera.isOpened():
            self.error = 'Impossible d’ouvrir la caméra. Vérifier la source et les permissions.'
            camera.release()
            return
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
        self.running = True
        try:
            while not self._stop.is_set():
                ok, frame = camera.read()
                if not ok:
                    self.error = 'Image indisponible depuis la caméra.'
                    break
                try:
                    detections = self.engine.process(frame)
                except Exception as exc:
                    logger.exception('Erreur de traitement vidéo')
                    self.error = str(exc)
                    break
                self._emit(frame, detections)
                time.sleep(.04)
        finally:
            camera.release()
            self.running = False
