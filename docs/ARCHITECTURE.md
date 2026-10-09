# KKB SECU · Architecture technique

**Architecture modulaire et testable** : le code source original est conservé dans `Ressources/` et la nouvelle interface principale est dans `kkbsecu/`.

```text
kkbsecu/
  config.py     -> Configuration injectée par environnement, chemins absolus
  storage.py    -> Repository SQLite : profils, journal d’événements, exports CSV
  vision.py     -> Détection OpenCV CPU et correspondance optionnelle par distance
  camera.py     -> Acquisition en thread dédié, file de dernière image non bloquante
  ui.py         -> Interfaces CustomTkinter (vues), orchestration des commandes
  __main__.py   -> CLI et lancement depuis python -m kkbsecu
scripts/
  audit_photos.py -> Décode et teste la détection sur les photos originales
  train.py        -> Enrôlement consenti explicite, fichier NPZ privé
runtime/           -> SQLite, gabarits privés, captures locales (ignorés par Git)
docs/screenshots/  -> Images originales fournies sans modification
```

## Choix et limites

- `cv2.CascadeClassifier` fonctionne sur CPU sans GPU. Si `face_recognition` est présent, la détection utilise HOG puis calcule une distance entre encodages.
- Correspondance positive si la **distance faciale** est sous un seuil ajustable, **sans prétendre** que cette valeur représente une probabilité ou une précision empirique.
- L'inférence d'âge, de sexe, d'émotion ou de personnalité n'est **pas implémentée**. Les textes et chiffres des captures servent de référence graphique, pas de résultats techniques.
- Les nouvelles identités, embeddings et journaux ne sont jamais ajoutés au dépôt Git : ils sont locaux dans `runtime/`.
- Les captures automatiques de visages non associés sont désactivées. Toute alerte doit être vérifiée par un opérateur.
- Limite de la version : ni contrôle d'accès matériel, ni anti-spoofing/liveness, ni chiffrement natif au repos, ni gestion multi-postes ou rôles durcis ; ne pas déployer comme dispositif de sécurité autonome sans audit.

## Réutilisation du code de départ

La nouvelle interface conserve le vocabulaire métier et l'intention de `main.py`, `Ressources/train.py` et `Ressources/final detect 1.0.py`, mais remplace leurs appels non reliés par une composition modulaire et des opérations testables.
