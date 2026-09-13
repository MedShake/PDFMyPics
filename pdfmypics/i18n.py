import gettext
import locale
import os


APP_NAME = "pdfmypics"


def initialiser_traduction():

    locale.setlocale(locale.LC_ALL, "")

    langue, _ = locale.getlocale()

    if langue:
        langue_gettext = langue.split("_")[0]
    else:
        langue_gettext = "en"

    repertoire = os.path.join(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        ),
        "locale"
    )

    traduction = gettext.translation(
        APP_NAME,
        localedir=repertoire,
        languages=[langue_gettext],
        fallback=True
    )

    traduction.install()


def formater_date(date):
    return date.strftime("%x %X")