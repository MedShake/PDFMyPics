from io import BytesIO

from PIL import Image, ImageOps

from reportlab.lib.pagesizes import (
    A4,
    landscape,
    portrait
)
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from .i18n import formater_date

DPI_HIGH = 300
POINTS_PER_INCH = 72


def creer_pdf(
    photos,
    fichier_pdf,
    colonnes,
    lignes,
    paysage,
    afficher_dates,
    progression_callback,
    dpi=DPI_HIGH
):
    page_width, page_height = (
        landscape(A4)
        if paysage
        else portrait(A4)
    )

    ratio_dpi = dpi / POINTS_PER_INCH

    pdf = canvas.Canvas(
        str(fichier_pdf),
        pagesize=(page_width, page_height)
    )

    marge = 24
    espace_x = 10
    espace_y = 16

    largeur_cellule_points = (
        page_width
        - 2 * marge
        - (colonnes - 1) * espace_x
    ) / colonnes

    hauteur_cellule_points = (
        page_height
        - 2 * marge
        - (lignes - 1) * espace_y
    ) / lignes

    photos_page = colonnes * lignes
    total = len(photos)

    if total == 0:
        pdf.save()
        return

    total_pages = (
        total + photos_page - 1
    ) // photos_page

    taille_texte_points = 7
    hauteur_reservee_texte_points = 12

    for index, photo in enumerate(photos):

        position = index % photos_page

        if position == 0 and index != 0:
            pdf.showPage()

        colonne = position % colonnes
        ligne = position // colonnes

        x_cellule = (
            marge
            + colonne * (
                largeur_cellule_points
                + espace_x
            )
        )

        y_cellule_base = (
            page_height
            - marge
            - (ligne + 1) * hauteur_cellule_points
            - ligne * espace_y
        )

        fichier = photo["fichier"]
        date = photo["date"]

        try:

            with Image.open(fichier) as image:

                image = ImageOps.exif_transpose(image)
                image = image.convert("RGB")

                largeur_originale, hauteur_originale = (
                    image.size
                )

                if afficher_dates:

                    hauteur_zone_image_points = (
                        hauteur_cellule_points
                        - hauteur_reservee_texte_points
                    )

                else:

                    hauteur_zone_image_points = (
                        hauteur_cellule_points
                    )

                largeur_cellule_pixels = (
                    largeur_cellule_points
                    * ratio_dpi
                )

                hauteur_zone_image_pixels = (
                    hauteur_zone_image_points
                    * ratio_dpi
                )

                ratio = min(
                    largeur_cellule_pixels
                    / largeur_originale,

                    hauteur_zone_image_pixels
                    / hauteur_originale
                )

                largeur_pixels = max(
                    1,
                    int(
                        largeur_originale
                        * ratio
                    )
                )

                hauteur_pixels = max(
                    1,
                    int(
                        hauteur_originale
                        * ratio
                    )
                )

                largeur_points = (
                    largeur_pixels
                    / ratio_dpi
                )

                hauteur_points = (
                    hauteur_pixels
                    / ratio_dpi
                )

                x_image = (
                    x_cellule
                    + (
                        largeur_cellule_points
                        - largeur_points
                    ) / 2
                )

                y_base_zone_image = (
                    y_cellule_base
                    + hauteur_reservee_texte_points
                    if afficher_dates
                    else y_cellule_base
                )

                y_image = (
                    y_base_zone_image
                    + (
                        hauteur_zone_image_points
                        - hauteur_points
                    ) / 2
                )

                buffer = BytesIO()

                image.thumbnail(
                    (
                        largeur_pixels,
                        hauteur_pixels
                    ),
                    Image.Resampling.LANCZOS
                )

                image.save(
                    buffer,
                    "JPEG",
                    quality=90,
                    optimize=True
                )

                buffer.seek(0)

                pdf.drawImage(
                    ImageReader(buffer),
                    x_image,
                    y_image,
                    width=largeur_points,
                    height=hauteur_points,
                    preserveAspectRatio=True,
                    mask="auto"
                )

            if afficher_dates:

                texte = (
                    formater_date(date)
                    if date
                    else _("date inconnue")
                )

                pdf.setFont(
                    "Helvetica",
                    taille_texte_points
                )

                y_texte = (
                    y_cellule_base
                    + hauteur_reservee_texte_points / 2
                    - taille_texte_points / 3
                )

                pdf.drawCentredString(
                    x_cellule
                    + largeur_cellule_points / 2,
                    y_texte,
                    texte
                )

        except Exception as erreur:

            print(
                _("Erreur :"),
                fichier,
                erreur
            )

        pourcentage = (
            (index + 1) / total
        )

        page_courante = (
            index // photos_page
        ) + 1

        progression_callback(
            pourcentage,
            _("Page %(page)d / %(total)d")
            % {
                "page": page_courante,
                "total": total_pages
            }
        )

    pdf.save()
