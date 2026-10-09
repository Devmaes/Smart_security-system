"""Computer-vision service: CPU detector, optional identity matching by consent.

Recognition is optional: no face embeddings are required for basic detection.
A face distance is NOT a calibrated probability or system accuracy.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from threading import RLock

import cv2
import numpy as np

try:
    import face_recognition  # type: ignore[import-not-found]
except ImportError:
    face_recognition = None


@dataclass(frozen=True, slots=True)
class FaceObservation:
    bbox: tuple[int, int, int, int]  # left, top, right, bottom
    user_id: str | None
    distance: float | None

    @property
    def label(self) -> str:
        return self.user_id or 'Visage non associé'


class FaceEngine:
    def __init__(self, templates_file: Path, threshold: float = 0.50):
        self.templates_file = Path(templates_file)
        self.threshold = threshold
        self._lock = RLock()
        self._ids: list[str] = []
        self._embeddings = np.empty((0, 128), dtype=np.float64)
        self._cascade = cv2.CascadeClassifier(
            str(Path(cv2.data.haarcascades) / 'haarcascade_frontalface_default.xml')
        )
        if self._cascade.empty():
            raise RuntimeError('OpenCV ne contient pas le détecteur Haar attendu')
        self.reload_templates()

    @property
    def matching_available(self) -> bool:
        return face_recognition is not None and bool(self._ids)

    def reload_templates(self) -> None:
        if not self.templates_file.exists():
            return
        # never allow pickle deserialization from untrusted .npy/.npz files.
        with np.load(self.templates_file, allow_pickle=False) as data:
            ids = np.asarray(data['ids'], dtype=str)
            vectors = np.asarray(data['vectors'], dtype=np.float64)
        if vectors.ndim != 2 or vectors.shape[1] != 128 or len(ids) != len(vectors):
            raise ValueError('Fichier de gabarits faciaux invalide')
        with self._lock:
            self._ids = ids.tolist()
            self._embeddings = vectors

    def _persist(self) -> None:
        self.templates_file.parent.mkdir(parents=True, exist_ok=True)
        with self._lock:
            temp = self.templates_file.with_suffix('.tmp.npz')
            np.savez_compressed(temp, ids=np.asarray(self._ids, dtype=str), vectors=self._embeddings)
            temp.replace(self.templates_file)
            try:
                self.templates_file.chmod(0o600)
            except OSError:
                pass

    def enroll(self, user_id: str, rgb_photo: np.ndarray, *, consent: bool) -> None:
        if not consent:
            raise PermissionError('Consentement requis pour enrôler un visage')
        if face_recognition is None:
            raise RuntimeError('Installer face_recognition pour activer l’enrôlement')
        encodings = face_recognition.face_encodings(rgb_photo)
        if len(encodings) != 1:
            raise ValueError('La photo doit contenir exactement un visage net')
        with self._lock:
            # Delete any previous enrollment for this ID while keeping vectors aligned.
            indices = [i for i, uid in enumerate(self._ids) if uid != user_id]
            self._embeddings = self._embeddings[indices]
            self._ids = [self._ids[i] for i in indices]
            self._ids.append(user_id)
            new = np.asarray(encodings[0], dtype=np.float64).reshape(1, 128)
            self._embeddings = np.vstack([self._embeddings, new])
            self._persist()

    def remove_template(self, user_id: str) -> None:
        with self._lock:
            indices = [i for i, value in enumerate(self._ids) if value != user_id]
            self._embeddings = self._embeddings[indices]
            self._ids = [self._ids[i] for i in indices]
            self._persist()

    def process(self, bgr: np.ndarray) -> list[FaceObservation]:
        if bgr is None or bgr.ndim != 3 or bgr.shape[2] != 3:
            raise ValueError('Image BGR attendue')
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        observations: list[FaceObservation] = []
        if face_recognition is not None:
            # Model HOG supports modest hardware without a GPU.
            locations = face_recognition.face_locations(rgb, model='hog')
            encodings = face_recognition.face_encodings(rgb, locations) if self._ids else []
            for i, (top, right, bottom, left) in enumerate(locations):
                uid, distance = None, None
                with self._lock:
                    if i < len(encodings) and len(self._embeddings):
                        dists = face_recognition.face_distance(self._embeddings, encodings[i])
                        best = int(np.argmin(dists))
                        distance = float(dists[best])
                        if distance <= self.threshold:
                            uid = self._ids[best]
                observations.append(FaceObservation((left, top, right, bottom), uid, distance))
        else:
            gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
            for x, y, w, h in self._cascade.detectMultiScale(gray, scaleFactor=1.12, minNeighbors=5, minSize=(42, 42)):
                observations.append(FaceObservation((int(x), int(y), int(x + w), int(y + h)), None, None))
        return observations


def annotate(frame: np.ndarray, detections: list[FaceObservation]) -> np.ndarray:
    output = frame.copy()
    for obs in detections:
        x1, y1, x2, y2 = obs.bbox
        color = (56, 211, 58) if obs.user_id else (49, 64, 248)
        cv2.rectangle(output, (x1, y1), (x2, y2), color, 2)
        cv2.putText(output, obs.label, (x1, max(y1 - 8, 18)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
    return output
