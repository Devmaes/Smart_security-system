# Plan de validation · KKB SECU

## Tests automatiques

- Contrôle syntaxique Python via `compileall`.
- Tests unitaires repository SQLite : ajout, recherche, suppression, journal, examen manuel d'un événement.
- Protection CSV contre l'injection de formules.
- Tests de détection d'une image artificielle vierge, d'erreurs de format et de décodage de photos déjà présentes sous `Images/`.
- Script `python scripts/audit_photos.py` pour produire un JSON de détection à partir de photos existantes. Ce test ne permet **pas** d'établir l'identité, la précision du système ou son niveau de sécurité.

## À tester sur machine avec webcam

- Autorisation d'accès caméra, ouverture/fermeture répétée, débranchement en fonctionnement.
- Écran de capture, changement thème, formulaire utilisateur, suppression et enrôlement explicite.
- Comparaison avec des photos d'évaluation consenties et séparées de l'entraînement.
- Vérifier la robustesse contre mauvaise luminosité, angles, occlusions, impressions/photo de téléphone.

## Ce qui n'est pas certifié

Aucune validation biométrique en production ou performance d'identification n'est attestée ici. La simple présence d'une bordure verte/rouge dans une capture ne prouve pas une reconnaissance correcte.
