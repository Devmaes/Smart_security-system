# KKB SECU · Facial Recognition & Computer Vision

**Système expérimental de supervision et d'analyse vidéo pour BKSquare SARL** — application de bureau construite en Python, OpenCV et CustomTkinter, optimisée pour des postes modestes.

> **Developed by Devmaes** · KKB SECU v3.0 · Projet privé

## Captures originales — sans modification

Les captures sont insérées **sans recadrage ni altération**. Elles constituent des maquettes de référence ; les données qu'elles montrent sont illustratives et ne préjugent pas de la précision du pipeline.

![Tableau de bord](docs/screenshots/Tableau%20de%20bord%20de%20reconnaissance%20faciale-1.png)

![Interface KKB SECU](docs/screenshots/Interface%20KKB%20SECU%20de%20reconnaissance%20faciale-2.png)

![Interface BKSquare](docs/screenshots/Interface%20BKSquare%20de%20reconnaissance%20faciale-3.png)

Le logo fourni est archivé sans modification sous `assets/branding/BK Square (1).png`.

## Fonctions

- Interface CustomTkinter sombre avec accents cyan/bleu et panneau de navigation.
- Accueil et métriques issues du journal SQLite (aucun compteur inventé).
- Détection vidéo OpenCV CPU, flux webcam/IP ou photo locale pour tests.
- Reconnaissance facultative si le module `face_recognition` et des gabarits consentis sont disponibles.
- Encadrement visuel des visages avec identifiant associé ou « Visage non associé ».
- Ajout et suppression de profils ; enrôlement optionnel avec consentement explicite.
- Liste des profils avec recherche, journal des événements, examen manuel des alertes.
- Export CSV, statistiques calculées et configuration documentée.
- Tests de non-régression et audit des photos existantes.

## Architecture & Tech Stack

| Couche | Technologies |
|---|---|
| Bureau | Python 3.11+, CustomTkinter, Pillow |
| Vision | OpenCV (Haar/HOG selon moteur), NumPy |
| Correspondance facultative | face_recognition (dlib), comparaison de distances |
| Données | SQLite (profil & événement), NPZ privé sans pickle |
| Tests | pytest, ruff, GitHub Actions |

Schéma détaillé : [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Installation Windows/Linux/macOS

```bash
git clone https://github.com/Devmaes/Smart_security-system.git
cd Smart_security-system
python -m venv .venv
```

Activation Windows : `.venv\\Scripts\\activate` ; Linux/macOS : `source .venv/bin/activate`.

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m kkbsecu
```

L'interface s'ouvre en mode détection par défaut. Pour une source caméra différente :

```bash
python -m kkbsecu --camera 1
python -m kkbsecu --demo-image "Images/im2.jpg"
```

Si le matériel et l'environnement le permettent, installer séparément `face-recognition` pour activer l'identification fondée sur des gabarits consentis. Ce module n'est **pas obligatoire** pour tester la détection sur CPU.

## Tester les images présentes dans le projet

```bash
pip install pytest opencv-python-headless numpy
pytest -q
python scripts/audit_photos.py --output runtime/photo_audit.json
```

Le script teste l'ouverture d'images et les détections OpenCV, **pas l'identité des personnes**.

## Enrôlement avec consentement

Créer d'abord l'identifiant dans l'interface, puis sélectionner une photo autorisée lors de l'assistant (si `face_recognition` est installé). Pour le mode CLI :

```bash
python scripts/train.py --user-id 001 --image /chemin/portrait_avec_consentement.jpg --consent-confirmed
```

Le gabarit est écrit dans `runtime/private/face_templates.npz`, ignoré par Git. Les fichiers d'encodages historiques sous `Pretrainement/` ne sont pas rechargés sans vérification : éviter `numpy.load(..., allow_pickle=True)` sur des données inconnues.

## Sécurité et limites

- Visage inconnu **≠ intrusion confirmée** : revue humaine avant tout signalement.
- Pas d'analyse d'âge, de sexe ou d'émotion inférée : ces informations des maquettes sont fictives.
- Les scores des captures (par exemple « 98 % ») sont illustratifs. **Aucun taux de reconnaissance réel n'a été certifié**.
- Les photos, données et journaux déjà suivis par Git dans l'ancien dépôt restent à auditer avant toute diffusion du repository.
- Sans anti-spoofing, chiffrement fort du poste et validation terrain, cet outil ne doit pas piloter seul un dispositif de sécurité physique.

Lire [SECURITY.md](docs/SECURITY.md), [TEST_REPORT.md](docs/TEST_REPORT.md) et [ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

**Developed by Devmaes** · BKSquare SARL · Python · OpenCV · Computer Vision
