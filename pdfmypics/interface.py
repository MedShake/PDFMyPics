import os
import threading
from io import BytesIO
from . import __version__

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GLib, GdkPixbuf, Gdk
from PIL import Image, ImageOps, ImageDraw, ImageFont
from . import i18n

def construire_interface(self):
    principal = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    self.fenetre.set_child(principal)

    contenu = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
    contenu.set_position(390)
    principal.append(contenu)

    # ========================================================
    # PANNEAU GAUCHE
    # ========================================================

    gauche_scroll = Gtk.ScrolledWindow()
    gauche_scroll.set_vexpand(True)
    contenu.set_start_child(gauche_scroll)

    gauche = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
    gauche.set_margin_top(25)
    gauche.set_margin_bottom(25)
    gauche.set_margin_start(25)
    gauche.set_margin_end(25)
    gauche_scroll.set_child(gauche)

    # ========================================================
    # TITRE
    # ========================================================

    titre = Gtk.Label(label=_("PDFMyPics"))
    titre.set_halign(Gtk.Align.START)
    titre.add_css_class("title-1")
    gauche.append(titre)

    description = Gtk.Label(
        label=_(
            "Créez rapidement des planches de vos photos "
            "classées par date sous forme de PDF."
        )
    )
    description.set_wrap(True)
    description.set_halign(Gtk.Align.START)
    description.add_css_class("dim-label")
    gauche.append(description)

    # ========================================================
    # CARTE PHOTOS
    # ========================================================

    carte = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    carte.add_css_class("card")
    gauche.append(carte)

    label = Gtk.Label(label=_("Photos"))
    label.set_halign(Gtk.Align.START)
    label.add_css_class("title-3")
    carte.append(label)

    self.label_dossier = Gtk.Label(label=_("Aucun dossier sélectionné"))
    self.label_dossier.set_wrap(True)
    self.label_dossier.set_halign(Gtk.Align.START)
    carte.append(self.label_dossier)

    bouton = Gtk.Button(label=_("📁 Choisir un dossier"))
    bouton.add_css_class("suggested-action")
    bouton.connect("clicked", self.choisir_dossier)
    carte.append(bouton)

    self.label_infos = Gtk.Label(label=_("Aucune photo chargée"))
    self.label_infos.set_halign(Gtk.Align.START)
    self.label_infos.add_css_class("dim-label")
    carte.append(self.label_infos)

    # ========================================================
    # MISE EN PAGE
    # ========================================================

    label = Gtk.Label(label=_("Mise en page"))
    label.set_halign(Gtk.Align.START)
    label.add_css_class("title-3")
    gauche.append(label)

    grille = Gtk.Grid()
    grille.set_column_spacing(10)
    grille.set_row_spacing(12)
    gauche.append(grille)

    # Colonnes
    grille.attach(Gtk.Label(label=_("Colonnes")), 0, 0, 1, 1)

    self.combo_colonnes = Gtk.DropDown.new_from_strings([str(i) for i in range(1, 10)])
    self.combo_colonnes.set_selected(3)
    self.combo_colonnes.connect("notify::selected", self.option_modifiee)

    grille.attach(self.combo_colonnes, 1, 0, 1, 1)

    # Lignes
    grille.attach(Gtk.Label(label=_("Lignes")), 2, 0, 1, 1)

    self.combo_lignes = Gtk.DropDown.new_from_strings([str(i) for i in range(1, 10)])
    self.combo_lignes.set_selected(2)
    self.combo_lignes.connect("notify::selected", self.option_modifiee)

    grille.attach(self.combo_lignes, 3, 0, 1, 1)

    # Orientation
    grille.attach(Gtk.Label(label=_("Orientation")), 0, 1, 1, 1)

    self.combo_orientation = Gtk.DropDown.new_from_strings([_("Paysage"), _("Portrait")])
    self.combo_orientation.set_selected(0)
    self.combo_orientation.connect("notify::selected", self.option_modifiee)

    grille.attach(self.combo_orientation, 1, 1, 3, 1)

    # Tri des dates
    grille.attach(Gtk.Label(label=_("Tri par dates")), 0, 2, 1, 1)

    self.combo_tri_date = Gtk.DropDown.new_from_strings(
        [_("Plus récentes → plus anciennes"), _("Plus anciennes → plus récentes")]
    )
    self.combo_tri_date.set_selected(0)
    self.combo_tri_date.connect("notify::selected", self.option_modifiee)

    grille.attach(self.combo_tri_date, 1, 2, 3, 1)

    # Dates
    self.check_dates = Gtk.CheckButton(label=_("Afficher date et heure"))
    self.check_dates.set_active(True)
    self.check_dates.connect("toggled", self.option_modifiee)
    gauche.append(self.check_dates)

    # ========================================================
    # FICHIER DE SORTIE
    # ========================================================

    label = Gtk.Label(label=_("Fichier de sortie"))
    label.set_halign(Gtk.Align.START)
    label.add_css_class("title-3")
    gauche.append(label)

    self.label_pdf = Gtk.Label(label=_("Aucun fichier PDF"))
    self.label_pdf.set_wrap(True)
    self.label_pdf.set_halign(Gtk.Align.START)
    self.label_pdf.add_css_class("dim-label")
    gauche.append(self.label_pdf)

    bouton_pdf = Gtk.Button(label=_("💾 Choisir le fichier PDF"))
    bouton_pdf.connect("clicked", self.choisir_pdf)
    gauche.append(bouton_pdf)

    # ========================================================
    # PROGRESSION
    # ========================================================

    self.label_progress = Gtk.Label(label=_("Prêt"))
    self.label_progress.set_halign(Gtk.Align.START)
    gauche.append(self.label_progress)

    self.progress = Gtk.ProgressBar()
    gauche.append(self.progress)

    # ========================================================
    # BOUTON CREER
    # ========================================================

    self.bouton_creer = Gtk.Button(label=_("Créer le PDF"))
    self.bouton_creer.add_css_class("suggested-action")
    self.bouton_creer.add_css_class("pill")
    self.bouton_creer.set_margin_top(10)
    self.bouton_creer.connect("clicked", self.lancer_generation)
    gauche.append(self.bouton_creer)

    # ========================================================
    # PANNEAU DROIT
    # ========================================================

    droite = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    droite.set_margin_top(20)
    droite.set_margin_bottom(20)
    droite.set_margin_start(20)
    droite.set_margin_end(20)
    contenu.set_end_child(droite)

    titre_preview = Gtk.Label(label=_("Prévisualisation"))
    titre_preview.add_css_class("title-2")
    titre_preview.set_halign(Gtk.Align.START)
    droite.append(titre_preview)

    self.preview = Gtk.Picture()
    self.preview.set_can_shrink(True)
    self.preview.set_content_fit(Gtk.ContentFit.CONTAIN)
    self.preview.set_vexpand(True)
    self.preview.set_hexpand(True)
    self.preview.add_css_class("preview-page")
    droite.append(self.preview)

    # ========================================================
    # NAVIGATION
    # ========================================================

    navigation = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    navigation.set_halign(Gtk.Align.CENTER)
    droite.append(navigation)

    precedent = Gtk.Button(label="‹")
    precedent.add_css_class("circular")
    precedent.connect("clicked", self.page_precedente)
    navigation.append(precedent)

    self.label_page = Gtk.Label(label=_("Page 0 / 0"))
    navigation.append(self.label_page)

    suivant = Gtk.Button(label="›")
    suivant.add_css_class("circular")
    suivant.connect("clicked", self.page_suivante)
    navigation.append(suivant)

    self.creer_apercu()

# ========================================================
# A PROPOS
# ========================================================

def afficher_a_propos(self):
    dialogue = Gtk.AboutDialog()

    dialogue.set_transient_for(self.fenetre)
    dialogue.set_modal(True)

    dialogue.set_program_name("PDFMyPics")
    dialogue.set_logo_icon_name("pdfmypics")
    dialogue.set_version(__version__)

    dialogue.set_authors([
        "Bertrand Boutillier <b.boutillier@gmail.com>"
    ])

    dialogue.set_license_type(
        Gtk.License.GPL_3_0
    )

    dialogue.set_license(
        _(
            "PDFMyPics est un logiciel libre distribué sous "
            "licence GNU General Public License version 3 ou ultérieure."
        )
    )

    dialogue.present()


def creer_apercu(self):
    if not self.photos:
        self.label_page.set_text(_("Aucune photo"))
        self.preview.set_paintable(None)
        return

    photos_page = self.colonnes * self.lignes

    total_pages = (len(self.photos) + photos_page - 1) // photos_page

    if self.page_apercu >= total_pages:
        self.page_apercu = 0

    debut = self.page_apercu * photos_page
    fin = min(debut + photos_page, len(self.photos))

    photos_page_liste = self.photos[debut:fin]

    self.label_page.set_text(
        _("Page %(page)d / %(total)d")
        % {
            "page": self.page_apercu + 1,
            "total": total_pages
        }
    )

    threading.Thread(
        target=self.generer_image_apercu, args=(photos_page_liste,), daemon=True
    ).start()


def generer_image_apercu(self, photos):
    largeur = 1000
    hauteur = 707 if self.paysage else 1414

    image_page = Image.new("RGB", (largeur, hauteur), "white")

    marge = 28
    espace_x = 12
    espace_y = 18

    largeur_cellule = (
        largeur - 2 * marge - (self.colonnes - 1) * espace_x
    ) / self.colonnes

    hauteur_cellule = (hauteur - 2 * marge - (self.lignes - 1) * espace_y) / self.lignes

    font = None

    for path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]:
        try:
            font = ImageFont.truetype(path, 10)
            break
        except IOError:
            continue

    if font is None:
        font = ImageFont.load_default()

    draw = ImageDraw.Draw(image_page)

    hauteur_reservee_texte = 25

    for position, photo in enumerate(photos):
        colonne = position % self.colonnes
        ligne = position // self.colonnes

        x_cellule = marge + colonne * (largeur_cellule + espace_x)

        y_cellule = marge + ligne * (hauteur_cellule + espace_y)

        try:
            with Image.open(photo["fichier"]) as source:
                source = ImageOps.exif_transpose(source)
                source = source.convert("RGB")

                hauteur_zone_image = (
                    hauteur_cellule - hauteur_reservee_texte
                    if self.afficher_dates
                    else hauteur_cellule
                )

                ratio = min(
                    largeur_cellule / source.width, hauteur_zone_image / source.height
                )

                nouvelle_largeur = max(1, int(source.width * ratio))

                nouvelle_hauteur = max(1, int(source.height * ratio))

                source.thumbnail(
                    (nouvelle_largeur, nouvelle_hauteur), Image.Resampling.LANCZOS
                )

                x = int(x_cellule + (largeur_cellule - nouvelle_largeur) / 2)

                y = int(y_cellule + (hauteur_zone_image - nouvelle_hauteur) / 2)

                image_page.paste(source, (x, y))

                if self.afficher_dates:
                    if photo["date"]:
                        texte = i18n.formater_date(photo["date"])
                    else:
                        texte = _("date inconnue")

                    font_utilisee = ImageFont.load_default()

                    w_zone = int(largeur_cellule)
                    h_zone = int(hauteur_reservee_texte)

                    txt_img = Image.new("RGBA", (w_zone, h_zone), (255, 255, 255, 0))

                    txt_draw = ImageDraw.Draw(txt_img)

                    try:
                        bbox = txt_draw.textbbox((0, 0), texte, font=font_utilisee)

                        tw = bbox[2] - bbox[0]
                        th = bbox[3] - bbox[1]

                    except Exception:
                        tw = 100
                        th = 10

                    tx = (w_zone - tw) // 2
                    ty = (h_zone - th) // 2

                    txt_draw.text((tx, ty), texte, font=font_utilisee, fill=(0, 0, 0))

                    px = int(x_cellule)
                    py = int(y_cellule + hauteur_cellule - hauteur_reservee_texte)

                    image_page.paste(txt_img, (px, py), txt_img)

        except Exception as erreur:
            print(_("Erreur aperçu :"), photo["fichier"], erreur)

    buffer = BytesIO()

    image_page.save(buffer, "PNG")

    buffer.seek(0)

    def afficher():
        try:
            loader = GdkPixbuf.PixbufLoader.new_with_type("png")

            loader.write(buffer.read())
            loader.close()

            pixbuf = loader.get_pixbuf()

            texture = Gdk.Texture.new_for_pixbuf(pixbuf)

            self.preview.set_paintable(texture)

        except Exception as erreur:
            print(_("Erreur affichage aperçu :"), erreur)

        return False

    GLib.idle_add(afficher)
