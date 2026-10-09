"""Safe, machine-independent paths and settings for KKB SECU."""
from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True, slots=True)
class Settings:
    data_dir: Path
    image_dir: Path
    camera_source: int | str = 0
    match_distance_threshold: float = 0.50
    detection_cooldown_seconds: float = 12.0
    save_unknown_crops: bool = False

    @property
    def db_path(self) -> Path:
        return self.data_dir / 'events.sqlite3'

    @property
    def embeddings_path(self) -> Path:
        return self.data_dir / 'private' / 'face_templates.npz'

    @classmethod
    def from_env(cls) -> 'Settings':
        source = os.getenv('KKBSECU_CAMERA', '0')
        source_parsed: int | str = int(source) if source.isdecimal() else source
        threshold = float(os.getenv('KKBSECU_MATCH_DISTANCE', '0.50'))
        if not 0.2 <= threshold <= 0.8:
            raise ValueError('KKBSECU_MATCH_DISTANCE doit être entre 0.2 et 0.8')
        return cls(
            data_dir=Path(os.getenv('KKBSECU_DATA_DIR', str(ROOT / 'runtime'))).expanduser(),
            image_dir=Path(os.getenv('KKBSECU_IMAGES_DIR', str(ROOT / 'Images'))).expanduser(),
            camera_source=source_parsed,
            match_distance_threshold=threshold,
            save_unknown_crops=False,
        )
