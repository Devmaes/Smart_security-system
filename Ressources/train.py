import os
import face_recognition
import numpy as np

pretrained_folder = r"C:\Users\_Maes\Desktop\KKB_SECU\Pretrainement"
known_faces_folder = r"C:\Users\_Maes\Desktop\soutenance 2k24\personnes connus"
encodings_file = os.path.join(pretrained_folder, "face_encodings.npy")
names_file = os.path.join(pretrained_folder, "face_names.npy")

def save_known_faces_encodings(known_faces_folder):
    known_face_encodings = []
    known_face_names = []
    
    for person_name in os.listdir(known_faces_folder):
        person_folder = os.path.join(known_faces_folder, person_name)
        if os.path.isdir(person_folder):
            for image_name in os.listdir(person_folder):
                image_path = os.path.join(person_folder, image_name)
                image = face_recognition.load_image_file(image_path)
                encoding = face_recognition.face_encodings(image)
                if encoding:
                    known_face_encodings.append(encoding[0])
                    known_face_names.append(person_name)
    
    # Sauvegarder les encodages et les noms dans des fichiers
    np.save(encodings_file, known_face_encodings)
    np.save(names_file, known_face_names)
    print("Encodages sauvegardés avec succès.")

# Vérifier si les fichiers existent déjà
if not os.path.exists(encodings_file) or not os.path.exists(names_file):
    save_known_faces_encodings(known_faces_folder)
