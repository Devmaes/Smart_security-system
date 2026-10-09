from pathlib import Path
import cv2
import numpy as np
import pytest
from kkbsecu.vision import FaceEngine, annotate


def test_empty_image_has_no_faces(tmp_path):
    engine = FaceEngine(tmp_path / 'private' / 'templates.npz')
    black_image = np.zeros((200, 200, 3), dtype=np.uint8)
    result = engine.process(black_image)
    assert result == []
    assert annotate(black_image, result).shape == black_image.shape


def test_invalid_image_rejected(tmp_path):
    engine = FaceEngine(tmp_path / 'templates.npz')
    with pytest.raises(ValueError):
        engine.process(np.zeros((30, 30), dtype=np.uint8))


def test_original_repository_photos_can_be_read(tmp_path):
    folder = Path(__file__).resolve().parents[1] / 'Images'
    photos = list(folder.glob('*.jpg')) + list(folder.glob('*.jpeg'))
    assert photos, 'Photos originales manquantes'
    decoded = sum(cv2.imread(str(photo)) is not None for photo in photos)
    assert decoded > 0
    # Deliberately do not assert any real person's identity based on an image.
