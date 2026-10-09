"""Opt-in enrollment via consented portrait folders. NEVER run on arbitrary photos."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sys

import cv2

from kkbsecu.config import Settings
from kkbsecu.vision import FaceEngine


def main() -> None:
    parser = argparse.ArgumentParser(description='Enrôler uniquement des personnes consentantes')
    parser.add_argument('--user-id', required=True, help='Identifiant préalablement créé dans l’application')
    parser.add_argument('--image', required=True, type=Path, help='Photo consentie contenant un visage')
    parser.add_argument('--consent-confirmed', action='store_true', help='Consentement documenté obtenu')
    args = parser.parse_args()
    if not args.consent_confirmed:
        parser.error('L’accord de la personne est indispensable : --consent-confirmed')
    image = cv2.imread(str(args.image))
    if image is None:
        parser.error('Photo illisible')
    engine = FaceEngine(Settings.from_env().embeddings_path)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    try:
        engine.enroll(args.user_id, rgb, consent=True)
    except (ValueError, RuntimeError, PermissionError) as exc:
        print(f'Enrôlement échoué : {exc}', file=sys.stderr)
        raise SystemExit(1) from exc
    print('Gabarit biométrique enregistré dans runtime/private, hors Git.')


if __name__ == '__main__':
    main()
