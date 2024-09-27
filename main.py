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
#foction de test
def Test():
    print("le test est bon bro !!!!")
    










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
main_frame = ctk.CTkFrame(fen,fg_color=None, border_width=5, border_color="Blue")
main_frame.pack(side="left", padx=10, pady=10, fill="y")

top_frame = ctk.CTkFrame(fen,fg_color="transparent", border_width=9, border_color="Blue")
top_frame.pack(side="top", fill="x", padx=10, pady=10, anchor = "center")

# Labels
lab1 = ctk.CTkLabel(fen, text="Mes Options", font=("Helvetica", 16, "bold"))
lab1.place(x=50, y=20)

lab3 = ctk.CTkLabel(top_frame, text="KKB", font=("Helvetica", 16, "bold"))
lab3.pack(side="left")

lab4 = ctk.CTkLabel(top_frame, text="SECU", font=("Helvetica", 16, "bold"))
lab4.pack(side="left")

# Toggle button
lab_tog = ctk.CTkLabel(top_frame, text="Dark", font=("Helvetica", 12, "bold"))
lab_tog.pack(side="right",padx = 0)

tog = ctk.CTkSwitch(top_frame, text="")
tog.pack()

# Label pour l'heure
time_label = ctk.CTkLabel(top_frame, font=('Helvetica', 24))
time_label.pack(side="bottom")
update_time()

# Icônes des boutons
icon_paths = {
    "Ajouter Utilisateur": "C:/Users/_Maes/Desktop/KKB_SECU/Icones/add-user.png",
    "Liste Des Utilisateurs": "C:/Users/_Maes/Desktop/KKB_SECU/Icones/phone-book.png",
    "Feuille d'enregistrement": "C:/Users/_Maes/Desktop/KKB_SECU/Icones/des-articles.png",
    "Intrusion": "C:/Users/_Maes/Desktop/KKB_SECU/Icones/thief.png",
    "Statistique": "C:/Users/_Maes/Desktop/KKB_SECU/Icones/statistiques.png",
    "Entrainement": "C:/Users/_Maes/Desktop/KKB_SECU/Icones/ai.png",
    "Configuration": "C:/Users/_Maes/Desktop/KKB_SECU/Icones/gear.png",
    "reconnaissance": "C:/Users/_Maes/Desktop/KKB_SECU/Icones/reconnaissance.png",
}

def create_button(parent, text, icon_path,fonc, fgcolor):
    icon_image = Image.open(icon_path)
    icon_image = icon_image.resize((20, 20))  # Redimensionner l'icône
    icon_photo = ImageTk.PhotoImage(icon_image)
    button = ctk.CTkButton(parent, text=text, width=200, height=50,image=icon_photo, compound="left",command=fonc, anchor ="center", fg_color=fgcolor )
    button.image = icon_photo  # Prévenir le garbage collector
    return button

# Boutons positionnés en bas de la première frame
main_frame.configure(fg_color='transparent')
but1 = create_button(main_frame, "Ajouter Utilisateur", icon_paths["Ajouter Utilisateur"],Test, "blue")
but1.pack(side="bottom", pady=10, padx=15)

but2 = create_button(main_frame, "Liste Des Utilisateurs", icon_paths["Liste Des Utilisateurs"],Test, "blue")
but2.pack(side="bottom", pady=3,padx=15)

but3 = create_button(main_frame, "Feuille d'enregistrement", icon_paths["Feuille d'enregistrement"],Test, "blue")
but3.pack(side="bottom", pady=5,padx=15)

but4 = create_button(main_frame, "Intrusion", icon_paths["Intrusion"],Test, "Dark blue")
but4.pack(side="bottom", pady=5,padx=15)

but5 = create_button(main_frame, "Statistique", icon_paths["Statistique"],Test, "Dark blue")
but5.pack(side="bottom", pady=5,padx=15)

but6 = create_button(main_frame, "Entrainement du module", icon_paths["Entrainement"],Test, "Dark Blue")
but6.pack(side="bottom", pady=5,padx=15)

but7 = create_button(main_frame, "Configuration", icon_paths["Configuration"],Test, "Dark Blue")
but7.pack(side="bottom", pady=5,padx=15)

# LabelFrame pour l'espace de travail
# lframe = ctk.CTkFrame(fen, corner_radius=10)
# lframe.pack(fill="both", expand=True, padx=10, pady=10)

# Bouton pour ouvrir une nouvelle fenêtre interne
open_window_button = create_button(fen, "Lancer RECONNAISSANCE", icon_paths["reconnaissance"],Test,"Dark green")
# open_window_button = ctk.CTkButton(fen, text="Lancer RECONNAISSANCE",  command=Test)
open_window_button.pack(pady=1)

fen.mainloop()
