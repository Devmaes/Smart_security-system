import customtkinter as ctk
import time
from PIL import Image, ImageTk

# Fonction pour mettre à jour l'heure
def update_time():
    current_time = time.strftime('%A, %Y-%m-%d %H:%M:%S')  # Ajout du jour de la semaine
    time_label.configure(text=current_time)
    time_label.after(1000, update_time)

# Fonction pour créer une nouvelle fenêtre
def Start():
    # Créer un nouveau frame à l'intérieur du LabelFrame
    new_window_frame = ctk.CTkFrame(lframe, fg_color="gray75")
    new_window_frame.pack(fill="both", expand=True, padx=5, pady=5)

    # Ajouter une étiquette au nouveau frame
    label = ctk.CTkLabel(new_window_frame, text="Ceci est une nouvelle fenêtre", font=("Helvetica", 14))
    label.pack(pady=10)

    # Ajouter un bouton de fermeture au nouveau frame
    close_button = ctk.CTkButton(new_window_frame, text="Fermer", command=new_window_frame.destroy)
    close_button.pack(pady=5)

    










#debut du main 

# Configuration de la fenêtre principale
fen = ctk.CTk()
fen.title("KKBSECU")
fen.geometry("1200x650")
fen.iconbitmap('C:/Users/_Maes/Desktop/GestCom/src/images/logo_kkbgestcom (1).ico')

# Ajouter une image d'arrière-plan
background_image = Image.open('C:/Users/_Maes/Desktop/soutenance 2k24/images photos/identification faciale .png')
background_image = background_image.resize((1200, 650))  # Redimensionner l'image pour couvrir toute la fenêtre
background_photo = ImageTk.PhotoImage(background_image)

background_label = ctk.CTkLabel(fen, image=background_photo)
background_label.place(x=0, y=0, relwidth=1, relheight=1)  # Couvrir toute la fenêtre

# Frame principale
main_frame = ctk.CTkFrame(fen)
main_frame.pack(side="left", padx=10, pady=10, fill="y")

top_frame = ctk.CTkFrame(fen)
top_frame.pack(side="top", fill="x", padx=10, pady=10)

# Labels
lab1 = ctk.CTkLabel(fen, text="Mes Options", font=("Helvetica", 16, "bold"))
lab1.place(x=50, y=20)

# lab2 = ctk.CTkLabel(fen, text="    ---", font=("Helvetica", 16, "bold"))
# lab2.place(x=50, y=40)

lab3 = ctk.CTkLabel(top_frame, text="KKB", font=("Helvetica", 16, "bold"))
lab3.pack(side="left")

lab4 = ctk.CTkLabel(top_frame, text="SECU", font=("Helvetica", 16, "bold"))
lab4.pack(side="left")

# Toggle button
lab_tog = ctk.CTkLabel(top_frame, text="Dark", font=("Helvetica", 12, "bold"))
lab_tog.pack(side="right")

tog = ctk.CTkSwitch(top_frame, text="")
tog.pack(side="right")

# Label pour l'heure
time_label = ctk.CTkLabel(top_frame, font=('Helvetica', 24))
time_label.pack(side="bottom")
update_time()

# Icônes des boutons
icon_paths = {
    "Ajouter Utilisateur": "C:/Users/_Maes/Desktop/GestCom/src/images/logo_kkbgestcom (2).ico",
    "Liste Des Utilisateurs": "C:/Users/_Maes/Desktop/GestCom/src/images/logo_kkbgestcom (2).ico",
    "Feuille d'enregistrement": "C:/Users/_Maes/Desktop/GestCom/src/images/logo_kkbgestcom (2).ico",
    "Intrusion": "C:/Users/_Maes/Desktop/GestCom/src/images/logo_kkbgestcom (2).ico",
    "Statistique": "C:/Users/_Maes/Desktop/GestCom/src/images/logo_kkbgestcom (2).ico",
    "Entrainement": "C:/Users/_Maes/Desktop/GestCom/src/images/logo_kkbgestcom (2).ico",
    "Configuration": "C:/Users/_Maes/Desktop/GestCom/src/images/logo_kkbgestcom (2).ico",
}

def create_button(parent, text, icon_path):
    icon_image = Image.open(icon_path)
    icon_image = icon_image.resize((20, 20))  # Redimensionner l'icône
    icon_photo = ImageTk.PhotoImage(icon_image)
    button = ctk.CTkButton(parent, text=text, width=200, height=50,image=icon_photo, compound="left")
    button.image = icon_photo  # Prévenir le garbage collector
    return button

# Boutons positionnés en bas de la première frame
but1 = create_button(main_frame, "Ajouter Utilisateur", icon_paths["Ajouter Utilisateur"])
but1.pack(side="bottom", pady=5)

but2 = create_button(main_frame, "Liste Des Utilisateurs", icon_paths["Liste Des Utilisateurs"])
but2.pack(side="bottom", pady=5)

but3 = create_button(main_frame, "Feuille d'enregistrement", icon_paths["Feuille d'enregistrement"])
but3.pack(side="bottom", pady=5)

but4 = create_button(main_frame, "Intrusion", icon_paths["Intrusion"])
but4.pack(side="bottom", pady=5)

but5 = create_button(main_frame, "Statistique", icon_paths["Statistique"])
but5.pack(side="bottom", pady=5)

but6 = create_button(main_frame, "Entrainement du module", icon_paths["Entrainement"])
but6.pack(side="bottom", pady=5)

but7 = create_button(main_frame, "Configuration", icon_paths["Configuration"])
but7.pack(side="bottom", pady=5)

# LabelFrame pour l'espace de travail
# lframe = ctk.CTkFrame(fen, corner_radius=10)
# lframe.pack(fill="both", expand=True, padx=10, pady=10)

# Bouton pour ouvrir une nouvelle fenêtre interne
open_window_button = ctk.CTkButton(fen, text="Lancer RECONNAISSANCE", command=Start)
open_window_button.pack(pady=10)

fen.mainloop()
