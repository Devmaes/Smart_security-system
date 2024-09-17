import customtkinter as ctk
import cv2
import face_recognition
import PIL.Image, PIL.ImageTk
import os

# Paramètres http://192.168.43.1:8080/video
# video_path = r"C:\Users\_Maes\Desktop\training ttkBoostrap GUI\vidjulios.mp4"
video_path = 0
# video_path = "http://192.168.43.1:8080/video"
output_folder = r"C:\Users\_Maes\Desktop\soutenance 2k24\images photos"
known_faces_folder = r"C:\Users\_Maes\Desktop\soutenance 2k24\personnes connus"
max_images_intrus = 15

# Définir cap comme variable globale
cap = None

# Créer la fenêtre principale
app = ctk.CTk()
app.geometry("1200x950")
app.title("Reconnaissance Faciale")

# Créer un cadre pour le canevas et la vidéo
video_frame = ctk.CTkFrame(app)
video_frame.pack(padx=20, pady=20, fill="both", expand=True)

# Créer un canevas pour afficher la vidéo
canvas = ctk.CTkCanvas(video_frame, width=800, height=500)
canvas.pack(side="left", fill="both", expand=True)

# Cadre pour afficher les images des personnes reconnues
known_image_frame = ctk.CTkFrame(app)
known_image_frame.pack(side="left", padx=20, pady=20)

# Créer des barres de défilement
scrollbar_y = ctk.CTkScrollbar(video_frame, orientation="vertical", command=canvas.yview)
scrollbar_y.pack(side="right", fill="y")

scrollbar_x = ctk.CTkScrollbar(video_frame, orientation="horizontal", command=canvas.xview)
scrollbar_x.pack(side="bottom", fill="x")

# Lier les barres de défilement au canevas
canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

# Créer un cadre dans le canevas pour contenir les images
content_frame = ctk.CTkFrame(canvas)
canvas.create_window((0, 0), window=content_frame, anchor="nw")

# Mettre à jour la zone visible du canevas
def update_scroll_region(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

canvas.bind("<Configure>", update_scroll_region)

# Charger les images des personnes connues et les encoder
def load_known_faces(known_faces_folder):
    known_face_encodings = []
    known_face_names = []
    known_face_images = {}  # Pour stocker les images des personnes connues
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
                    # Charger l'image connue
                    pil_image = PIL.Image.open(image_path)
                    pil_image.thumbnail((150, 150))  # Redimensionner l'image
                    known_face_images[person_name] = PIL.ImageTk.PhotoImage(pil_image)
    return known_face_encodings, known_face_names, known_face_images

known_face_encodings, known_face_names, known_face_images = load_known_faces(known_faces_folder)

# Liste pour stocker les chemins des images des intrus sauvegardées
saved_images_intrus = []
recognized_name = None  # Pour vérifier si une personne est reconnue

# Fonction pour arrêter la capture vidéo et afficher un message
def stop_video_with_message():
    global cap
    if cap is not None and cap.isOpened():
        cap.release()  # Arrêter la capture vidéo
    canvas.delete("all")
    message_label = ctk.CTkLabel(app, text="Fin de la reconnaissance", font=("Arial", 20))
    message_label.pack()

# Fonction pour traiter le frame et effectuer la reconnaissance faciale
def process_frame():
    global saved_images_intrus, recognized_name, cap

    # Vérifier si la capture est encore ouverte
    if cap is None or not cap.isOpened():
        return
    
    ret, frame = cap.read()
    if not ret:
        cap.release()
        return
    
    # Convertir l'image BGR en RGB pour face_recognition
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Détection des visages
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Comparer avec les visages connus
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "intrus !"
        color = (0, 0, 255)  # Rouge pour les intrus
        
        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]
            color = (0, 255, 0)  # Vert pour les visages reconnus

            # Si une personne est reconnue et ce n'est pas la même personne précédente
            if name != recognized_name:
                recognized_name = name
                # Afficher la photo de la personne reconnue
                if name in known_face_images:
                    known_image_label = ctk.CTkLabel(known_image_frame, image=known_face_images[name], text=name)
                    known_image_label.pack()
        
        # Dessiner des rectangles autour des visages et ajouter le texte
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, name, (left, bottom + 20), font, 0.75, color, 2)

        # Sauvegarder les images des intrus détectés
        if name == "intrus !" and len(saved_images_intrus) < max_images_intrus:
            intrus_img = frame[top:bottom, left:right]
            intrus_path = os.path.join(output_folder, f"intrus_{len(saved_images_intrus) + 1}.png")
            cv2.imwrite(intrus_path, intrus_img)
            saved_images_intrus.append(intrus_path)

    # Convertir l'image OpenCV en image PIL
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_img = PIL.Image.fromarray(frame_rgb)
    tk_img = PIL.ImageTk.PhotoImage(pil_img)

    # Afficher l'image dans le canevas
    canvas.create_image(0, 0, anchor="nw", image=tk_img)
    canvas.image = tk_img  # Garder une référence pour éviter la destruction de l'image

    # Appeler la fonction de traitement du prochain frame
    app.after(10, process_frame)

# Fonction pour démarrer la reconnaissance faciale
def start_recognition():
    global cap
    cap = cv2.VideoCapture(video_path)  # Initialiser la capture vidéo ici
    process_frame()  # Appeler la fonction de traitement des frames
    # Arrêter la reconnaissance faciale après 1 minute
    app.after(700000, stop_video_with_message)

# Démarrer la reconnaissance faciale après 10 secondes de lecture vidéo
app.after(5000, start_recognition)

# Lancer l'application
app.mainloop()
