import os
import threading

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gio, GLib, Gtk

from .interface import (
    afficher_a_propos,
    construire_interface,
    creer_apercu,
    generer_image_apercu,
)
from .pdf import DPI_HIGH, creer_pdf
from .photos import lire_photos, trier_photos


class PDFMyPicsApp(Gtk.Application):

    def __init__(self):

        super().__init__(
            application_id="fr.pdfmypics.app",
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )

        self.fenetre = None

        self.dossier = None
        self.photos = []
        self.fichier_pdf = None

        # Configuration par défaut

        self.colonnes = 4
        self.lignes = 3
        self.paysage = True
        self.afficher_dates = True

        # Tri :
        # desc = plus récent → plus ancien
        # asc  = plus ancien → plus récent

        self.ordre_date = "desc"

        self.page_apercu = 0

        # Widgets

        self.label_dossier = None
        self.label_infos = None
        self.label_pdf = None

        self.combo_colonnes = None
        self.combo_lignes = None
        self.combo_orientation = None
        self.combo_tri_date = None

        self.check_dates = None

        self.preview = None
        self.label_page = None

        self.progress = None
        self.label_progress = None

        self.bouton_creer = None

    # ========================================================
    # ACTIVATION
    # ========================================================

   
    def do_activate(self):

        if self.fenetre is None:

            self.fenetre = Gtk.ApplicationWindow(
                application=self
            )

            self.fenetre.set_default_size(
                1200,
                850
            )

            self.fenetre.set_size_request(
                950,
                700
            )

            # ====================================================
            # BARRE DE TITRE
            # ====================================================

            barre = Gtk.HeaderBar()

            titre = Gtk.Label(label="PDFMyPics")
            titre.add_css_class("title-2")

            barre.set_title_widget(titre)

            # ====================================================
            # ACTION "À PROPOS"
            # ====================================================

            action_apropos = Gio.SimpleAction.new(
                "about",
                None
            )

            action_apropos.connect(
                "activate",
                self.action_apropos
            )

            self.add_action(action_apropos)

            # ====================================================
            # MENU HAMBURGER
            # ====================================================

            menu = Gio.Menu.new()

            menu.append(
                "À propos de PDFMyPics",
                "app.about"
            )

            menu.append(
                "Quitter",
                "app.quit"
            )

            # ====================================================
            # ACTION "QUITTER"
            # ====================================================

            action_quitter = Gio.SimpleAction.new(
                "quit",
                None
            )

            action_quitter.connect(
                "activate",
                lambda action, param: self.quit()
            )

            self.add_action(action_quitter)

            # ====================================================
            # BOUTON HAMBURGER
            # ====================================================

            bouton_menu = Gtk.MenuButton()

            bouton_menu.set_icon_name(
                "open-menu-symbolic"
            )

            bouton_menu.set_tooltip_text(
                "Menu"
            )

            bouton_menu.set_menu_model(
                menu
            )

            barre.pack_end(
                bouton_menu
            )

            self.fenetre.set_titlebar(
                barre
            )

            # ====================================================
            # INTERFACE
            # ====================================================

            construire_interface(self)

        self.fenetre.present()



    # ========================================================
    # À PROPOS
    # ========================================================

    def action_apropos(self, action, parametre=None): 
        afficher_a_propos(self)


    # ========================================================
    # DOSSIER
    # ========================================================

    def choisir_dossier(self, bouton):

        dialogue = Gtk.FileDialog.new()

        dialogue.set_title(
            "Choisir le dossier des photos"
        )

        dialogue.select_folder(
            self.fenetre,
            None,
            self.dossier_selectionne
        )

    def dossier_selectionne(
        self,
        dialogue,
        resultat
    ):

        try:

            fichier = (
                dialogue.select_folder_finish(
                    resultat
                )
            )

            self.dossier = fichier.get_path()

            self.label_dossier.set_text(
                self.dossier
            )

            self.label_infos.set_text(
                "Analyse des photos..."
            )

            threading.Thread(
                target=self.scanner,
                daemon=True
            ).start()

        except Exception:
            pass

    # ========================================================
    # SCAN
    # ========================================================

    def scanner(self):

        photos = lire_photos(
            self.dossier
        )

        self.photos = trier_photos(
            photos,
            self.ordre_date
        )

        GLib.idle_add(
            self.scan_termine
        )

    def scan_termine(self):

        total = len(
            self.photos
        )

        exif = sum(
            1
            for photo in self.photos
            if photo["date"]
        )

        self.label_infos.set_text(
            f"{total} photos — {exif} dates EXIF"
        )

        if self.dossier:

            self.fichier_pdf = os.path.join(
                self.dossier,
                "planche_photos.pdf"
            )

            self.label_pdf.set_text(
                self.fichier_pdf
            )

        self.page_apercu = 0

        self.creer_apercu()

        return False

    # ========================================================
    # OPTIONS
    # ========================================================

    def option_modifiee(self, *args):

        self.colonnes = (
            self.combo_colonnes.get_selected()
            + 1
        )

        self.lignes = (
            self.combo_lignes.get_selected()
            + 1
        )

        self.paysage = (
            self.combo_orientation.get_selected()
            == 0
        )

        self.ordre_date = (
            "desc"
            if self.combo_tri_date.get_selected() == 0
            else "asc"
        )

        self.afficher_dates = (
            self.check_dates.get_active()
        )

        self.photos = trier_photos(
            self.photos,
            self.ordre_date
        )

        self.page_apercu = 0

        self.creer_apercu()

    # ========================================================
    # CHOIX PDF
    # ========================================================

    def choisir_pdf(self, bouton):

        dialogue = Gtk.FileDialog.new()

        dialogue.set_title(
            "Enregistrer le PDF"
        )

        dialogue.save(
            self.fenetre,
            None,
            self.pdf_selectionne
        )

    def pdf_selectionne(
        self,
        dialogue,
        resultat
    ):

        try:

            fichier = (
                dialogue.save_finish(
                    resultat
                )
            )

            chemin = fichier.get_path()

            if not chemin.lower().endswith(".pdf"):
                chemin += ".pdf"

            self.fichier_pdf = chemin

            self.label_pdf.set_text(
                chemin
            )

        except Exception:
            pass

    # ========================================================
    # APERCU
    # ========================================================

    def creer_apercu(self):
        creer_apercu(self)

    def generer_image_apercu(self, photos):
        generer_image_apercu(
            self,
            photos
        )

    # ========================================================
    # NAVIGATION
    # ========================================================

    def page_precedente(self, bouton):

        if not self.photos:
            return

        if self.page_apercu > 0:

            self.page_apercu -= 1

            self.creer_apercu()

    def page_suivante(self, bouton):

        if not self.photos:
            return

        photos_page = (
            self.colonnes
            * self.lignes
        )

        total_pages = (
            len(self.photos)
            + photos_page
            - 1
        ) // photos_page

        if self.page_apercu < (
            total_pages - 1
        ):

            self.page_apercu += 1

            self.creer_apercu()

    # ========================================================
    # GENERATION PDF
    # ========================================================

    def lancer_generation(self, bouton):

        if not self.photos:

            self.message(
                "Aucune photo",
                "Sélectionnez d'abord un dossier contenant vos photos."
            )

            return

        if not self.fichier_pdf:

            self.message(
                "Fichier PDF",
                "Choisissez le fichier PDF de destination."
            )

            return

        self.bouton_creer.set_sensitive(
            False
        )

        self.progress.set_fraction(0)

        self.label_progress.set_text(
            "Création du PDF..."
        )

        threading.Thread(
            target=self.generation_thread,
            daemon=True
        ).start()

    def generation_thread(self):

        try:

            creer_pdf(
                self.photos,
                self.fichier_pdf,
                self.colonnes,
                self.lignes,
                self.paysage,
                self.afficher_dates,
                self.progression_pdf,
                dpi=DPI_HIGH
            )

            GLib.idle_add(
                self.pdf_termine
            )

        except Exception as erreur:

            GLib.idle_add(
                self.pdf_erreur,
                str(erreur)
            )

    # ========================================================
    # PROGRESSION
    # ========================================================

    def progression_pdf(
        self,
        valeur,
        texte
    ):

        GLib.idle_add(
            self.actualiser_progression,
            valeur,
            texte
        )

    def actualiser_progression(
        self,
        valeur,
        texte
    ):

        self.progress.set_fraction(
            valeur
        )

        self.label_progress.set_text(
            texte
        )

        return False

    # ========================================================
    # FIN PDF
    # ========================================================

    def pdf_termine(self):

        self.progress.set_fraction(1)

        self.label_progress.set_text(
            "✓ PDF créé avec succès"
        )

        self.bouton_creer.set_sensitive(
            True
        )

        self.message(
            "PDF terminé",
            f"Le fichier a été créé :\n\n{self.fichier_pdf}"
        )

        return False

    def pdf_erreur(self, erreur):

        self.bouton_creer.set_sensitive(
            True
        )

        self.label_progress.set_text(
            "Erreur"
        )

        self.message(
            "Erreur",
            erreur
        )

        return False

    # ========================================================
    # MESSAGE
    # ========================================================

    def message(
        self,
        titre,
        texte
    ):

        dialogue = Gtk.AlertDialog()

        dialogue.set_message(
            titre
        )

        dialogue.set_detail(
            texte
        )

        def dialogue_ferme(dialogue, resultat):

            try:
                dialogue.choose_finish(resultat)

                self.progress.set_fraction(0)

                self.label_progress.set_text(
                    "Prêt"
                )

            except GLib.Error:
                pass

        dialogue.choose(
            self.fenetre,
            None,
            dialogue_ferme
        )