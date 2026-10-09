# Publier la refonte dans Devmaes/Smart_security-system

Cette archive contient le code modulaire, les ressources historiques utiles et les **images originales sans retouche**.

Si vous préférez publier vous-même les images depuis un poste disposant des autorisations GitHub :

```bash
git clone https://github.com/Devmaes/Smart_security-system.git
cd Smart_security-system
git switch -c feature/kkbsecu-v3
# Copier le contenu de l'archive à la racine du dépôt cloné, sans le dossier racine du ZIP.
git status
git add .gitignore README.md main.py requirements*.txt pyproject.toml kkbsecu scripts tests docs assets .github
# Les fichiers de l'ancien code et les photos dans Images/ peuvent déjà être suivis.
git commit -m "feat: refactor KKB SECU with modular computer vision and desktop UI"
git push -u origin feature/kkbsecu-v3
```

Demander la revue de la branche avant fusion dans `main`. Ne pas committer `runtime/`, les nouveaux gabarits biométriques ni des fichiers de données réelles ; vérifier les anciennes données déjà suivies et l'historique.
