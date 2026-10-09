# Protection des données biométriques

Les photographies de visages, gabarits et événements de reconnaissance sont des données personnelles sensibles.

1. N'enrôler une personne qu'avec un fondement légitime et une information claire. L'application exige une confirmation de consentement pour l'enrôlement.
2. **Aucun inconnu n'est automatiquement une intrusion.** Le système affiche « Visage non associé » ; tout signalement nécessite un examen humain.
3. Le stockage SQLite et les NPZ sous `runtime/` sont exclus de Git ; utiliser un poste chiffré, un contrôle des accès OS, une politique de conservation courte et une procédure de suppression des données.
4. Les modèles biométriques peuvent être attaqués ; `allow_pickle=False` évite une désérialisation arbitraire dans le nouveau lecteur.
5. **Historique existant à auditer :** le dépôt source contient déjà des fichiers `Pretrainement/face_encodings.npy`, `face_names.npy`, des journaux `.txt` et des photos de personnes. Ajouter un `.gitignore` ne les efface ni du HEAD ni de l'historique. Il faut décider de leur retrait/réécriture avec les responsables des données. Ne jamais prétendre qu'ils ont été supprimés sans vérification.
6. Les planches UI envoyées par le demandeur sont incluses telles quelles, sans retouches ; elles comportent potentiellement des visages reconnaissables. Ne pas rendre le dépôt public sans confirmation des droits et autorisations.
7. Les indicateurs 98 % / 87 % dans des maquettes ne sont pas des mesures expérimentales. Un benchmark réel exige un jeu de test consenti distinct, des définitions de FAR/FRR, des analyses de biais et des scénarios de terrain.

**Pas de mot de passe de démonstration en clair**, pas de journalisation de secrets, pas de reconnaissance clandestine.
