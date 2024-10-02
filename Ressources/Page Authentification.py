import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import messagebox

# Fonction de fermeture de l'application
def close_app():
    fen.destroy()

        
# Fonction pour gérer l'oubli du mot de passe
def forgot_password():
    # Ajoutez ici la logique pour traiter le mot de passe oublié
    print("Mot de passe oublié")
def on_enter(e):
    entry_username.delete(0,'end')
    
def on_leave(e):
    name = entry_username.get()
    if name == '':
        entry_username.insert(0,'Username')

        
          
        
# Configuration de la fenêtre principale
fen = ctk.CTk()
fen.title("Formulaire de Connexion")
fen.geometry("800x500")
fen.iconbitmap('C:/Users/_Maes/Desktop/GestCom/src/images/logo_kkbgestcom (1).ico')
fen.resizable(False,False)
fen.configure(set_appearance_mode = "light", fg_color= "white")



# Fonction pour gérer la connexion
def login():
    username = entry_username.get()
    password = entry_password.get()
    # Ajoutez ici la logique pour traiter la connexion
    print(f"Nom d'utilisateur: {username}, Mot de passe: {password}")
    if username == 'admin' and password =='1234':
        screen =ctk.CTkToplevel(fen) 
        screen.title("validateur")
        screen.geometry('925x500+300')
        screen.configure(bg_colour ="white")
        lab_t = ctk.CTkLabel(screen,text=f"wellcome {username} JULIOS MAES",text_color='white', font=('Microsoft YaHei UI Light',30,'bold'))
        lab_t.pack()
        screen.mainloop()  
    else:
        messagebox.showerror("Erreur", "Nom d'utilisateur ou mot de passe incorrect...")



#image 
imageL_path = "C:/Users/_Maes/Desktop/KKB_SECU/Images/login1.jpg"
imageL = Image.open(imageL_path).resize((450,400))
photoL = ImageTk.PhotoImage(imageL)
image_label = ctk.CTkLabel(fen, image=photoL, text="")
image_label.place(x=60, y=50)

#principal frame
fr = ctk.CTkFrame(fen,height=400,fg_color="white")
fr.place(x=550,y=50)
  

#label titel connect
heading = ctk.CTkLabel(fr, text='Se Connecter',text_color='#57a1f8',fg_color='transparent',font=('Microsoft YaHei UI Light',35,'bold'))
heading.pack(pady=2)

# Label pour le nom d'utilisateur
label_username = ctk.CTkLabel(fr, text="Nom d'utilisateur:",text_color='black')
label_username.pack(pady=2)

# Champ de saisie pour le nom d'utilisateur
entry_username = ctk.CTkEntry(fr,width=200,height=40,border_color='#57a1f8',fg_color='white',text_color='grey')
entry_username.pack(pady=5)
entry_username.insert(0,'Veillez entrer votre nom...')
entry_username.bind('<FocusIn>', on_enter)
entry_username.bind('<FocusOut>', on_leave)
# Label pour le mot de passe
label_password = ctk.CTkLabel(fr, text="Mot de passe:",text_color='black')
label_password.pack(pady=10)


# Champ de saisie pour le mot de passe
entry_password = ctk.CTkEntry(fr, show="*",width=200,height=40,border_color='#57a1f8',fg_color='white',text_color='grey')
entry_password.pack(pady=10)



# Bouton de connexion
login_button = ctk.CTkButton(fr, text="Se connecter", command=login,width=200,height=40,fg_color='#57a1f8')
login_button.pack(pady=10)

# Bouton mot de passe oublié
forgot_button = ctk.CTkButton(fr, text="Mot de passe oublié", command=forgot_password,width=200,height=40,fg_color='#57a1f8')
forgot_button.pack(pady=10)

# Bouton fermer
close_button = ctk.CTkButton(fr, text="Fermer", command=close_app,width=150,height=40,fg_color='dark red')
close_button.pack(pady=10)

fen.mainloop()
