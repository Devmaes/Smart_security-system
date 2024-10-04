import pyttsx3

# Initialiser l'engine
engine = pyttsx3.init()

# Récupérer les voix disponibles
voices = engine.getProperty('voices')

# Choisir une voix masculine (si disponible)
for voice in voices:
    if "male" in voice.name.lower():  # ou "Male" selon ton système
        engine.setProperty('voice', voice.id)
        print(f"Voix masculine sélectionnée: {voice.name}")
        break

# Convertir un texte en parole
engine.say("Bonjour, je suis une voix masculine.   Dany  et avec julios  a la maison")
engine.runAndWait()
