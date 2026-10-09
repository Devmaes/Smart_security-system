"""Check original image files using OpenCV; never infer someone's identity."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import cv2

from kkbsecu.config import ROOT


def audit(folder: Path) -> dict[str, object]:
    cascade = cv2.CascadeClassifier(str(Path(cv2.data.haarcascades) / 'haarcascade_frontalface_default.xml'))
    if cascade.empty():
        raise RuntimeError('Détecteur Haar indisponible')
    extensions = {'.png', '.jpg', '.jpeg', '.webp'}
    paths = sorted(p for p in folder.iterdir() if p.suffix.lower() in extensions and p.is_file())
    reports = []
    for path in paths:
        frame = cv2.imread(str(path))
        if frame is None:
            reports.append({'file': path.name, 'decoded': False, 'faces_detected': 0})
            continue
        # CPU-friendly bounded resolution for high-resolution originals.
        height, width = frame.shape[:2]
        if max(height, width) > 900:
            scale = 900 / max(height, width)
            frame = cv2.resize(frame, (round(width * scale), round(height * scale)), interpolation=cv2.INTER_AREA)
        grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        boxes = cascade.detectMultiScale(grayscale, scaleFactor=1.12, minNeighbors=5, minSize=(42, 42))
        reports.append({'file': path.name, 'decoded': True, 'faces_detected': len(boxes)})
    return {
        'analyzed': len(reports),
        'readable': sum(1 for x in reports if x['decoded']),
        'photos_with_face_detections': sum(1 for x in reports if x['faces_detected']),
        'files': reports,
        'disclaimer': 'Ces détections ne mesurent ni reconnaissance, ni identité, ni précision globale.',
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--images', type=Path, default=ROOT / 'Images')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = audit(args.images)
    result = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result + '\n', encoding='utf-8')
    print(result)


if __name__ == '__main__':
    main()
