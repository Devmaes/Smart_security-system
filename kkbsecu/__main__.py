"""Entry point: python -m kkbsecu [--demo-image PATH]."""
from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path

from .config import Settings


def main() -> None:
    parser = argparse.ArgumentParser(description='KKB SECU · BKSquare SARL')
    parser.add_argument('--demo-image', type=Path, help='Tester une photo existante hors ligne')
    parser.add_argument('--camera', help='Indice ou adresse du flux vidéo')
    args = parser.parse_args()
    settings = Settings.from_env()
    if args.demo_image:
        if not args.demo_image.is_file():
            parser.error('Photo de démonstration introuvable')
        settings = replace(settings, camera_source=str(args.demo_image.resolve()))
    elif args.camera:
        source: int | str = int(args.camera) if args.camera.isdecimal() else args.camera
        settings = replace(settings, camera_source=source)

    from .ui import SecurityApp
    app = SecurityApp(settings)
    app.mainloop()


if __name__ == '__main__':
    main()
