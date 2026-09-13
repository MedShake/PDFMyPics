import os
from datetime import datetime

from PIL import Image


def obtenir_date_exif(fichier):
    try:
        with Image.open(fichier) as image:
            exif = image.getexif()

            for tag in (36867, 36868, 306):
                valeur = exif.get(tag)

                if valeur:
                    try:
                        return datetime.strptime(
                            str(valeur),
                            "%Y:%m:%d %H:%M:%S"
                        )
                    except ValueError:
                        pass

    except Exception:
        pass

    return None


def lire_photos(dossier):
    extensions = (
        ".jpg",
        ".jpeg",
        ".JPG",
        ".JPEG"
    )

    photos = []

    for nom in os.listdir(dossier):

        if not nom.endswith(extensions):
            continue

        chemin = os.path.join(
            dossier,
            nom
        )

        if not os.path.isfile(chemin):
            continue

        date = obtenir_date_exif(chemin)

        photos.append({
            "fichier": chemin,
            "date": date
        })

    return photos


def trier_photos(photos, ordre="desc"):
    """
    Trie les photos selon leur date EXIF.

    Les photos sans date EXIF sont toujours placées à la fin.
    """

    photos_triees = list(photos)

    if ordre == "asc":

        photos_triees.sort(
            key=lambda p: (
                p["date"] is None,
                p["date"] or datetime.min
            )
        )

    else:

        photos_triees.sort(
            key=lambda p: (
                p["date"] is None,
                -p["date"].timestamp()
                if p["date"]
                else 0
            )
        )

    return photos_triees