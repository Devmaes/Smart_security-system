"""Desktop operator interface inspired by original KKB SECU screenshots.

Developed by Devmaes. Presentation only: all application logic lives in
storage.py, vision.py and camera.py. Unmatched faces are not automatically
classified as intruders; an operator must review an event.
"""
from __future__ import annotations

from collections import deque
from datetime import datetime
from pathlib import Path
import time
from tkinter import filedialog, messagebox, ttk

import cv2
import customtkinter as ctk
from PIL import Image

from .camera import CameraWorker
from .config import ROOT, Settings
from .storage import Repository, User
from .vision import FaceEngine, FaceObservation, annotate

NAVY = '#06162A'
DEEP = '#061021'
PANEL = '#0B243A'
PANEL_ALT = '#0D2B45'
BORDER = '#1D526B'
CYAN = '#12C8F5'
BLUE = '#087CF5'
WHITE = '#F3F9FE'
MUTED = '#8BAEC3'
GREEN = '#1CD18E'
RED = '#FF5363'

ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('blue')


class SecurityApp(ctk.CTk):
    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.repo = Repository(settings.db_path)
        self.engine = FaceEngine(settings.embeddings_path, settings.match_distance_threshold)
        self.worker: CameraWorker | None = None
        self._last_event: dict[str, float] = {}
        self._latest_frame = None
        self._latest_detections: list[FaceObservation] = []
        self._preview_photo = None
        self._display_photo = None
        self._demo_source: Path | None = None
        self._current_page = ''
        self._nav: dict[str, ctk.CTkButton] = {}
        self._recent_activity: deque[str] = deque(maxlen=20)
        self._draft_image: Path | None = None
        self._draft_photo = None
        self._draft_user: tuple[str, str, str] | None = None
        self._enroll_step = 1
        self.title('KKB SECU V3.0 | BKSquare SARL · Developed by Devmaes')
        self.geometry('1400x860')
        self.minsize(1090, 680)
        self.configure(fg_color=DEEP)
        self.protocol('WM_DELETE_WINDOW', self._close)
        self._build_shell()
        self.show('Accueil')
        self.after(1000, self._tick_clock)
        self.after(140, self._poll_camera)

    def _build_shell(self) -> None:
        self.sidebar = ctk.CTkFrame(self, width=230, fg_color=NAVY, corner_radius=0)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)
        logo_path = ROOT / 'Icones' / 'logo_KKB.png'
        if logo_path.exists():
            logo_img = Image.open(logo_path).convert('RGBA')
            self._logo_ctk = ctk.CTkImage(logo_img, size=(144, 130))
            ctk.CTkLabel(self.sidebar, image=self._logo_ctk, text='').pack(pady=(22, 4))
        else:
            ctk.CTkLabel(self.sidebar, text='BK SQUARE', font=('Arial', 26, 'bold'), text_color=CYAN).pack(pady=30)
        ctk.CTkLabel(self.sidebar, text='KKB SECU   V3.0', text_color=CYAN, font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        ctk.CTkLabel(self.sidebar, text='MES OPTIONS', anchor='w', width=185,
                     text_color=MUTED, font=('Arial', 11, 'bold')).pack(pady=(0, 12))
        items = [
            ('Accueil', '⌂'), ('Détection en direct', '◉'), ('Utilisateurs', '♙'),
            ('Ajouter un utilisateur', '⊕'), ('Intrusions', '⚠'),
            ('Journal des accès', '▤'), ('Statistiques', '▥'), ('Configuration', '⚙'),
        ]
        for name, symbol in items:
            btn = ctk.CTkButton(
                self.sidebar, text=f'{symbol}   {name}', anchor='w', height=41,
                width=208, corner_radius=8, border_spacing=12,
                fg_color='transparent', hover_color='#0C3D5B', text_color=WHITE,
                font=('Arial', 12, 'bold'), command=lambda n=name: self.show(n),
            )
            btn.pack(padx=10, pady=3)
            self._nav[name] = btn
        ctk.CTkLabel(self.sidebar, text='Developed by Devmaes', text_color=MUTED,
                     font=('Arial', 11)).pack(side='bottom', pady=24)
        self.right = ctk.CTkFrame(self, fg_color=DEEP, corner_radius=0)
        self.right.pack(side='right', fill='both', expand=True)
        self.header = ctk.CTkFrame(self.right, height=65, fg_color=NAVY, corner_radius=0,
                                   border_color=BORDER, border_width=1)
        self.header.pack(fill='x')
        self.header.pack_propagate(False)
        ctk.CTkLabel(self.header, text='BKSquare    /    KKB SECU', text_color=CYAN,
                     font=('Arial', 19, 'bold')).pack(side='left', padx=24)
        self.clock = ctk.CTkLabel(self.header, text='', font=('Arial', 12), text_color=WHITE)
        self.clock.pack(side='left', padx=12)
        self.theme_switch = ctk.CTkSwitch(self.header, text='Mode sombre', width=90,
                                          command=self._set_theme)
        self.theme_switch.select()
        self.theme_switch.pack(side='right', padx=24)
        self.content = ctk.CTkFrame(self.right, fg_color=DEEP, corner_radius=0)
        self.content.pack(fill='both', expand=True, padx=20, pady=18)

    def _set_theme(self) -> None:
        ctk.set_appearance_mode('dark' if self.theme_switch.get() else 'light')

    def _tick_clock(self) -> None:
        if not self.winfo_exists():
            return
        self.clock.configure(text=datetime.now().strftime('%d/%m/%Y  %H:%M:%S'))
        self.after(1000, self._tick_clock)

    def _clear(self) -> None:
        for widget in self.content.winfo_children():
            widget.destroy()

    def show(self, page: str) -> None:
        if page != 'Détection en direct' and self.worker is not None:
            self._stop_camera()
        self._current_page = page
        self._clear()
        for name, btn in self._nav.items():
            btn.configure(fg_color=BLUE if name == page else 'transparent')
        routes = {
            'Accueil': self._home,
            'Détection en direct': self._live,
            'Utilisateurs': self._users,
            'Ajouter un utilisateur': self._enroll,
            'Intrusions': self._alerts,
            'Journal des accès': self._journal,
            'Statistiques': self._stats,
            'Configuration': self._config,
        }
        routes[page]()

    def _heading(self, title: str, description: str = '') -> None:
        ctk.CTkLabel(self.content, text=title, font=('Arial', 27, 'bold'), text_color=WHITE,
                     anchor='w').pack(fill='x', padx=8, pady=(0, 2))
        if description:
            ctk.CTkLabel(self.content, text=description, text_color=MUTED,
                         font=('Arial', 12), anchor='w').pack(fill='x', padx=8, pady=(0, 18))

    def _panel(self, parent, title: str | None = None, *, fill='both', expand=True):
        panel = ctk.CTkFrame(parent, fg_color=PANEL, border_color=BORDER,
                             border_width=1, corner_radius=14)
        panel.pack(fill=fill, expand=expand, padx=7, pady=7)
        if title:
            ctk.CTkLabel(panel, text=title, font=('Arial', 16, 'bold'),
                         text_color=WHITE, anchor='w').pack(fill='x', padx=17, pady=(14, 8))
        return panel

    def _button(self, parent, text: str, command, *, color=BLUE, width=185):
        return ctk.CTkButton(parent, text=text, command=command, fg_color=color,
                             hover_color='#0559C7', height=39, width=width,
                             corner_radius=8, font=('Arial', 12, 'bold'))

    def _stat_tile(self, parent, amount: int | str, title: str, color=CYAN) -> None:
        tile = ctk.CTkFrame(parent, fg_color=PANEL_ALT, corner_radius=12,
                            border_color=BORDER, border_width=1)
        tile.pack(side='left', expand=True, fill='both', padx=6, pady=8)
        ctk.CTkLabel(tile, text=str(amount), font=('Arial', 28, 'bold'),
                     text_color=color).pack(pady=(20, 0))
        ctk.CTkLabel(tile, text=title, font=('Arial', 12), text_color=WHITE).pack(pady=(0, 18))

    def _home(self) -> None:
        self._heading('SYSTÈME DE RECONNAISSANCE FACIALE', 'KKB SECU V3.0 · Tableau de bord opérateur')
        hero = ctk.CTkFrame(self.content, height=230, fg_color=NAVY,
                            border_color=BORDER, border_width=1, corner_radius=16)
        hero.pack(fill='x', padx=7, pady=(0, 12))
        hero.pack_propagate(False)
        left = ctk.CTkFrame(hero, fg_color='transparent')
        left.pack(side='left', fill='both', expand=True, padx=25, pady=22)
        ctk.CTkLabel(left, text='KKB SECU V3.0', font=('Arial', 31, 'bold'),
                     text_color=CYAN).pack(anchor='w', pady=(6, 3))
        ctk.CTkLabel(left, text='Détection, contrôle d’accès et supervision locale',
                     font=('Arial', 14), text_color=WHITE).pack(anchor='w', pady=8)
        self._button(left, '▶  Lancer la reconnaissance',
                     lambda: self.show('Détection en direct'), width=270).pack(anchor='w', pady=12)
        wallpaper = ROOT / 'Images' / 'identification faciale .png'
        if wallpaper.is_file():
            self._hero_image = ctk.CTkImage(Image.open(wallpaper), size=(300, 200))
            ctk.CTkLabel(hero, text='', image=self._hero_image).pack(side='right', padx=16)
        metrics = ctk.CTkFrame(self.content, fg_color='transparent')
        metrics.pack(fill='x', padx=5)
        stats = self.repo.statistics()
        self._stat_tile(metrics, stats['recognized'], 'Détections associées', GREEN)
        self._stat_tile(metrics, stats['unknown'], 'Visages non associés', RED)
        self._stat_tile(metrics, stats['users'], 'Utilisateurs enregistrés', CYAN)
        self._stat_tile(metrics, stats['total'], 'Événements enregistrés', '#A7A0FF')
        panel = self._panel(self.content, 'Dernières détections')
        self._render_events(panel, self.repo.list_events(6))

    def _render_events(self, parent, events) -> None:
        if not events:
            ctk.CTkLabel(parent, text='Aucun événement enregistré. Démarrez une analyse pour commencer.',
                         text_color=MUTED).pack(pady=28)
        for event in events:
            line = ctk.CTkFrame(parent, fg_color=PANEL_ALT, corner_radius=8)
            line.pack(fill='x', padx=15, pady=4)
            status_color = GREEN if event.status == 'recognized' else RED if event.status == 'alert' else CYAN
            ctk.CTkLabel(line, text=event.label, anchor='w', text_color=WHITE,
                         font=('Arial', 12, 'bold')).pack(side='left', padx=12, pady=8)
            ctk.CTkLabel(line, text=event.status.upper(), text_color=status_color,
                         font=('Arial', 11, 'bold')).pack(side='left', padx=14)
            ctk.CTkLabel(line, text=event.occurred_at[:19].replace('T', ' '),
                         text_color=MUTED).pack(side='right', padx=12)

    def _live(self) -> None:
        self._heading('Détection en temps réel',
                      'OpenCV · modèle HOG sur CPU si face_recognition est installé · source locale ou vidéo')
        actions = ctk.CTkFrame(self.content, fg_color='transparent')
        actions.pack(fill='x', padx=6)
        self._button(actions, '▶ Démarrer la caméra', self._start_camera, width=180).pack(side='left', padx=5)
        self._button(actions, '■ Arrêter', self._stop_camera, color='#43566A', width=130).pack(side='left', padx=5)
        self._button(actions, '▣ Tester une photo', self._choose_demo, width=180).pack(side='left', padx=5)
        self._button(actions, '▣ Capturer une image', self._save_snapshot, width=195).pack(side='left', padx=5)
        self.status_label = ctk.CTkLabel(actions, text='● En attente', text_color=MUTED)
        self.status_label.pack(side='right', padx=15)
        main = ctk.CTkFrame(self.content, fg_color='transparent')
        main.pack(fill='both', expand=True)
        video_panel = ctk.CTkFrame(main, fg_color=PANEL, border_color=BORDER,
                                   border_width=1, corner_radius=14)
        video_panel.pack(side='left', fill='both', expand=True, padx=7, pady=7)
        ctk.CTkLabel(video_panel, text='Flux vidéo / image source',
                     font=('Arial', 16, 'bold'), text_color=WHITE).pack(anchor='w', padx=17, pady=(14, 8))
        self.preview = ctk.CTkLabel(video_panel, text='Caméra inactive\n\nCliquer sur « Démarrer » ou « Tester une photo »',
                                    font=('Arial', 16), text_color=MUTED)
        self.preview.pack(fill='both', expand=True, padx=14, pady=14)
        info = ctk.CTkFrame(main, width=275, fg_color=PANEL, corner_radius=12,
                            border_color=BORDER, border_width=1)
        info.pack(side='right', fill='y', pady=7)
        info.pack_propagate(False)
        ctk.CTkLabel(info, text='PROFIL DE DÉTECTION', font=('Arial', 15, 'bold'),
                     text_color=CYAN).pack(pady=(20, 12))
        self.face_label = ctk.CTkLabel(info, text='Aucun visage analysé', text_color=WHITE,
                                       justify='left', font=('Arial', 14))
        self.face_label.pack(anchor='w', padx=17, pady=10)
        ctk.CTkLabel(info, text='Une distance faciale n’est pas une\nprobabilité de confiance.',
                     justify='left', font=('Arial', 11), text_color=MUTED).pack(padx=14, pady=20)
        self._button(info, 'Voir le journal', lambda: self.show('Journal des accès'),
                     width=240).pack(pady=(16, 7))
        self._button(info, 'Signaler pour examen', self._flag_latest_unknown,
                     color='#B52946', width=240).pack(pady=7)
        self._start_camera()

    def _choose_demo(self) -> None:
        source = filedialog.askopenfilename(
            title='Photo de démonstration (test local)',
            initialdir=str(self.settings.image_dir),
            filetypes=[('Images', '*.jpg *.jpeg *.png *.webp')],
        )
        if source:
            self._demo_source = Path(source)
            self._start_camera()

    def _start_camera(self) -> None:
        self._stop_camera()
        source = str(self._demo_source) if self._demo_source else self.settings.camera_source
        self.worker = CameraWorker(self.engine, source)
        self.worker.start()
        if hasattr(self, 'status_label'):
            self.status_label.configure(text='● Initialisation...', text_color=CYAN)

    def _stop_camera(self) -> None:
        if self.worker:
            self.worker.stop()
            self.worker = None
        if hasattr(self, 'status_label') and self._current_page == 'Détection en direct':
            self.status_label.configure(text='● Inactif', text_color=MUTED)

    def _poll_camera(self) -> None:
        if not self.winfo_exists():
            return
        if self.worker and self._current_page == 'Détection en direct':
            result = self.worker.latest()
            if result:
                frame, detections = result
                self._latest_frame = frame.copy()
                self._latest_detections = detections
                self._display_video(annotate(frame, detections))
                self.status_label.configure(text='● Flux reçu', text_color=GREEN)
                self._render_observation(detections)
                self._maybe_log(detections)
            elif self.worker.error:
                self.status_label.configure(text='● ' + self.worker.error[:50], text_color=RED)
        self.after(130, self._poll_camera)

    def _display_video(self, bgr) -> None:
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        original = Image.fromarray(rgb)
        max_w = max(self.preview.winfo_width() - 20, 350)
        max_h = max(self.preview.winfo_height() - 20, 300)
        original.thumbnail((max_w, max_h))
        self._display_photo = ctk.CTkImage(light_image=original, dark_image=original,
                                            size=original.size)
        self.preview.configure(image=self._display_photo, text='')

    def _render_observation(self, observations: list[FaceObservation]) -> None:
        if not observations:
            self.face_label.configure(text='Aucun visage détecté')
            return
        lines = [f'Visages détectés : {len(observations)}']
        for n, observation in enumerate(observations[:5], 1):
            lines.append(f'\nVisage {n} : {observation.label}')
            if observation.distance is not None:
                lines.append(f'Distance faciale : {observation.distance:.3f}')
        self.face_label.configure(text='\n'.join(lines))

    def _maybe_log(self, observations: list[FaceObservation]) -> None:
        now = time.monotonic()
        for obs in observations:
            status = 'recognized' if obs.user_id else 'unknown'
            key = obs.user_id or '_unknown'
            if now - self._last_event.get(key, -1000) < self.settings.detection_cooldown_seconds:
                continue
            self.repo.log(obs.label, obs.user_id, obs.distance, status)
            self._last_event[key] = now

    def _flag_latest_unknown(self) -> None:
        events = self.repo.list_events(1, status='unknown')
        if not events:
            messagebox.showinfo('Vérification', 'Aucun événement non associé à examiner.')
            return
        if messagebox.askyesno('Revue humaine', 'Signaler le dernier visage inconnu comme événement à examiner ?'):
            self.repo.mark_alert(events[0].event_id)
            messagebox.showinfo('Enregistré', 'Signalement enregistré, sans déclenchement automatique d’alarme.')

    def _save_snapshot(self) -> None:
        if self._latest_frame is None:
            messagebox.showinfo('Capture', 'Aucune image disponible.')
            return
        if not messagebox.askyesno('Donnée personnelle', 'Enregistrer explicitement cette image localement ?'):
            return
        path = filedialog.asksaveasfilename(defaultextension='.png', filetypes=[('Image PNG', '*.png')])
        if path:
            if cv2.imwrite(path, self._latest_frame):
                messagebox.showinfo('Capture', 'Image enregistrée à l’emplacement choisi.')
            else:
                messagebox.showerror('Erreur', 'Impossible d’enregistrer cette image.')

    def _users(self) -> None:
        self._heading('Liste des utilisateurs', 'Gestion locale et recherche des profils enregistrés')
        bar = ctk.CTkFrame(self.content, fg_color='transparent')
        bar.pack(fill='x', padx=6, pady=8)
        self.search = ctk.CTkEntry(bar, placeholder_text='Rechercher par nom ou identifiant...', width=350)
        self.search.pack(side='left', padx=6)
        self._button(bar, 'Rechercher', lambda: self._populate_users(), width=110).pack(side='left', padx=4)
        self._button(bar, '+ Ajouter un utilisateur', lambda: self.show('Ajouter un utilisateur'), width=220).pack(side='right')
        self.user_list = self._panel(self.content, 'Utilisateurs enregistrés')
        self._populate_users()

    def _populate_users(self) -> None:
        for child in self.user_list.winfo_children()[1:]:
            child.destroy()
        users = self.repo.list_users(self.search.get())
        if not users:
            ctk.CTkLabel(self.user_list, text='Aucun utilisateur dans la base locale.', text_color=MUTED).pack(pady=25)
        for user in users:
            row = ctk.CTkFrame(self.user_list, fg_color=PANEL_ALT, corner_radius=8)
            row.pack(fill='x', padx=16, pady=6)
            ctk.CTkLabel(row, text=user.user_id, width=100, text_color=CYAN).pack(side='left', padx=7, pady=9)
            ctk.CTkLabel(row, text=user.name, text_color=WHITE, width=190, anchor='w').pack(side='left', padx=8)
            ctk.CTkLabel(row, text=user.role, text_color=MUTED, width=130).pack(side='left', padx=8)
            ctk.CTkLabel(row, text='Actif' if user.active else 'Inactif', text_color=GREEN if user.active else RED).pack(side='left')
            self._button(row, 'Supprimer', lambda uid=user.user_id: self._remove_user(uid),
                         width=105, color='#A62D49').pack(side='right', padx=9)

    def _remove_user(self, user_id: str) -> None:
        if messagebox.askyesno('Suppression', f'Supprimer le profil {user_id} et son gabarit facial local ?'):
            self.engine.remove_template(user_id)
            self.repo.delete_user(user_id)
            self._populate_users()

    def _enroll(self) -> None:
        self._heading('Ajouter un nouvel utilisateur',
                      'Assistant : 1. Informations  →  2. Photo avec consentement  →  3. Confirmation')
        self._draft_user = None
        self._draft_image = None
        self._enroll_step = 1
        self.enroll_panel = self._panel(self.content, 'Informations générales')
        self._enroll_step_info()

    def _enroll_step_info(self) -> None:
        p = self.enroll_panel
        ctk.CTkLabel(p, text='Nom complet *', anchor='w').pack(padx=23, fill='x', pady=(18, 4))
        self.enroll_name = ctk.CTkEntry(p, width=460, placeholder_text='Ex. Jean Dupont')
        self.enroll_name.pack(anchor='w', padx=23)
        ctk.CTkLabel(p, text='ID unique *', anchor='w').pack(padx=23, fill='x', pady=(17, 4))
        self.enroll_id = ctk.CTkEntry(p, width=460, placeholder_text='Ex. 002')
        self.enroll_id.pack(anchor='w', padx=23)
        ctk.CTkLabel(p, text='Rôle *', anchor='w').pack(padx=23, fill='x', pady=(17, 4))
        self.enroll_role = ctk.CTkComboBox(p, values=['Employé', 'Administrateur', 'Visiteur'], width=460)
        self.enroll_role.pack(anchor='w', padx=23)
        self._button(p, 'Suivant  →', self._enroll_next, width=200).pack(anchor='e', padx=23, pady=28)

    def _enroll_next(self) -> None:
        user = (self.enroll_id.get().strip(), self.enroll_name.get().strip(), self.enroll_role.get().strip())
        if any(not x for x in user):
            messagebox.showerror('Formulaire', 'Tous les champs obligatoires doivent être renseignés.')
            return
        if any(x.user_id == user[0] for x in self.repo.list_users()):
            messagebox.showerror('ID existant', 'Cet identifiant est déjà enregistré.')
            return
        self._draft_user = user
        for w in self.enroll_panel.winfo_children()[1:]:
            w.destroy()
        ctk.CTkLabel(self.enroll_panel, text='Capture et consentement', text_color=CYAN,
                     font=('Arial', 21, 'bold')).pack(anchor='w', padx=24, pady=18)
        ctk.CTkLabel(self.enroll_panel,
                     text='Choisissez une photo de la personne concernée, avec son accord explicite.\n'
                          'L’enrôlement biométrique est facultatif : le profil peut être créé sans photo.',
                     justify='left', text_color=WHITE).pack(anchor='w', padx=24, pady=8)
        self.consent_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self.enroll_panel, text='La personne a donné son consentement à l’enrôlement biométrique',
                        variable=self.consent_var).pack(anchor='w', padx=24, pady=18)
        self.photo_name = ctk.CTkLabel(self.enroll_panel, text='Aucune photo sélectionnée', text_color=MUTED)
        self.photo_name.pack(anchor='w', padx=24)
        self._button(self.enroll_panel, 'Choisir une photo', self._pick_enroll_photo,
                     width=210).pack(anchor='w', padx=24, pady=12)
        self._button(self.enroll_panel, 'Créer le profil  →', self._finish_enroll,
                     width=220).pack(anchor='e', padx=24, pady=28)

    def _pick_enroll_photo(self) -> None:
        path = filedialog.askopenfilename(title='Photo autorisée', initialdir=str(self.settings.image_dir),
                                           filetypes=[('Images', '*.jpg *.jpeg *.png')])
        if path:
            self._draft_image = Path(path)
            self.photo_name.configure(text=self._draft_image.name)

    def _finish_enroll(self) -> None:
        assert self._draft_user is not None
        uid, name, role = self._draft_user
        if self._draft_image and not self.consent_var.get():
            messagebox.showerror('Consentement', 'Cochez le consentement ou créez le profil sans photo.')
            return
        if self._draft_image:
            img = cv2.imread(str(self._draft_image))
            if img is None:
                messagebox.showerror('Image', 'Impossible de lire cette photo.')
                return
            try:
                self.engine.enroll(uid, cv2.cvtColor(img, cv2.COLOR_BGR2RGB), consent=True)
            except Exception as exc:
                messagebox.showerror('Enrôlement', f'Erreur : {exc}')
                return
        try:
            self.repo.add_user(User(uid, name, role))
        except Exception as exc:
            # Undo a previously created template if the metadata insert failed.
            if self._draft_image:
                self.engine.remove_template(uid)
            messagebox.showerror('Enregistrement', str(exc))
            return
        messagebox.showinfo('Profil créé', 'Profil enregistré dans la base locale.')
        self.show('Utilisateurs')

    def _journal(self) -> None:
        self._heading('Feuille d’enregistrement', 'Traçabilité locale des détections — horodatages UTC')
        actions = ctk.CTkFrame(self.content, fg_color='transparent')
        actions.pack(fill='x')
        self._button(actions, 'Exporter en CSV', self._export).pack(side='right', padx=8)
        panel = self._panel(self.content, 'Événements récents')
        self._render_events(panel, self.repo.list_events(100))

    def _export(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV', '*.csv')])
        if path:
            try:
                self.repo.export_csv(Path(path))
                messagebox.showinfo('Export', 'Fichier CSV généré.')
            except OSError as exc:
                messagebox.showerror('Export', str(exc))

    def _alerts(self) -> None:
        self._heading('Événements à examiner',
                      'Un visage non associé ne constitue pas automatiquement une intrusion.')
        panel = self._panel(self.content, 'Signalements examinés par un opérateur')
        self._render_events(panel, self.repo.list_events(100, status='alert'))
        unknown = self.repo.list_events(1, status='unknown')
        if unknown:
            self._button(panel, 'Examiner le dernier événement inconnu', self._flag_latest_unknown,
                         color='#B52946', width=340).pack(pady=20)

    def _stats(self) -> None:
        self._heading('Statistiques et rapports', 'Résultats locaux réels, sans pourcentages de confiance inventés')
        metrics = ctk.CTkFrame(self.content, fg_color='transparent')
        metrics.pack(fill='x')
        stats = self.repo.statistics()
        self._stat_tile(metrics, stats['recognized'], 'Associations')
        self._stat_tile(metrics, stats['unknown'], 'Non associés', RED)
        self._stat_tile(metrics, stats['users'], 'Utilisateurs', CYAN)
        self._stat_tile(metrics, stats['total'], 'Captures journalisées', GREEN)
        panel = self._panel(self.content, 'Répartition des événements')
        bars = ctk.CTkFrame(panel, fg_color='transparent')
        bars.pack(fill='both', expand=True, padx=25, pady=16)
        entries = [('Associés', stats['recognized'], GREEN),
                   ('Non associés', stats['unknown'], CYAN),
                   ('Signalés', stats['alert'], RED)]
        total = max(stats['total'], 1)
        for label, count, color in entries:
            ctk.CTkLabel(bars, text=f'{label} : {count}', text_color=WHITE,
                         anchor='w').pack(fill='x', pady=(14, 4))
            ctk.CTkProgressBar(bars, progress_color=color, fg_color=PANEL_ALT,
                               height=16).pack(fill='x')
            bar = bars.winfo_children()[-1]
            bar.set(count / total)
        self._button(panel, 'Exporter les événements', self._export, width=220).pack(pady=18)

    def _config(self) -> None:
        self._heading('Configuration', 'Paramètres de la station locale — confidentialité et caméra')
        p = self._panel(self.content, 'Paramètres actifs')
        config_items = [
            ('Caméra', str(self.settings.camera_source)),
            ('Base locale', str(self.settings.db_path)),
            ('Gabarits privés', str(self.settings.embeddings_path)),
            ('Distance maximale de correspondance', str(self.engine.threshold)),
            ('Reconnaissance optionnelle', 'Disponible' if self.engine.matching_available else 'Détection seulement'),
            ('Captures automatiques de visages non associés', 'Désactivées'),
        ]
        for title, value in config_items:
            row = ctk.CTkFrame(p, fg_color=PANEL_ALT)
            row.pack(fill='x', padx=15, pady=5)
            ctk.CTkLabel(row, text=title, width=250, anchor='w', text_color=MUTED).pack(side='left', padx=12, pady=8)
            ctk.CTkLabel(row, text=value, anchor='w', text_color=WHITE).pack(side='left', padx=10)
        ctk.CTkLabel(
            p, text='Modifier KKBSECU_CAMERA et KKBSECU_MATCH_DISTANCE dans les variables d’environnement.\n'
                    'Ne jamais committer des images de personnes, gabarits ou logs privés.',
            justify='left', text_color=CYAN,
        ).pack(anchor='w', padx=17, pady=22)

    def _close(self) -> None:
        self._stop_camera()
        self.destroy()
