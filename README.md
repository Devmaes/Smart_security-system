# KKBSECU — prototype privé de reconnaissance faciale

Ce dépôt rassemble une interface Python et des scripts expérimentaux de reconnaissance faciale pour un projet de contrôle d'accès. Il reste privé en raison des données et ressources associées.

## Structure actuelle

- `main.py` : écran d'accueil en CustomTkinter. Plusieurs boutons appellent encore une fonction de test ; le bouton « Lancer RECONNAISSANCE » n'ouvre pas le script de reconnaissance dans ce snapshot.
- `Ressources/train.py` : génération d'encodages à partir d'images locales.
- `Ressources/final detect 1.0.py` : acquisition vidéo, comparaison avec les encodages, affichage et journalisation.
- `Pretrainement/` : fichiers d'encodages et journaux déjà présents dans l'historique du dépôt ; à traiter comme des données sensibles.

## Reproduction et limites

L'écran `main.py` utilise maintenant les images et icônes du dépôt avec des chemins relatifs. Les scripts de `Ressources/` utilisent encore des chemins absolus Windows propres à la machine de développement. Ils nécessitent notamment Python, CustomTkinter, Pillow, OpenCV, `face_recognition`, NumPy et une caméra. Aucun fichier de dépendances verrouillées ni protocole d'évaluation n'est fourni ici : ce snapshot ne permet pas de vérifier un taux de reconnaissance ni un niveau de sécurité.

Avant toute démonstration, remplacer les chemins absolus, travailler avec des données de test consenties et anonymisées, définir les dépendances et consigner les conditions de mesure. Ne pas publier les encodages, noms, journaux ou images réels.

## Suite de travail

Relier l'interface au module de reconnaissance, isoler la configuration, documenter les erreurs de reconnaissance et préparer une démonstration expurgée avec l'autorisation de l'entreprise.