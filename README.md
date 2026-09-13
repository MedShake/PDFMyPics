# PDFMyPics

**PDFMyPics** is a lightweight Linux desktop application for quickly creating PDF photo contact sheets from a folder of images.

![PDFMyPics](screenshot.png)

## Installation

### Debian package (`.deb`)

The **recommended way to install PDFMyPics** is to use the Debian package provided in the project's Releases.

Download the latest `pdfmypics_..._all.deb` package and install it with:

```bash
sudo apt install ./pdfmypics_0.1.0_all.deb
```
The package also installs the application icon, desktop launcher, and translations (Tests made with Linux Mint).

### Updating

New versions are published as `.deb` packages in the project's Releases.

Download the new package and install it using the same command:

```bash
sudo apt install ./pdfmypics_VERSION_all.deb
```

## Usage

Launch PDFMyPics from the application menu.

1. Select the folder containing your photos.
2. Choose the page orientation.
3. Set the number of rows and columns.
4. Choose the photo sorting order.
5. Enable or disable photo dates.
6. Preview the result.
7. Choose the output PDF file.
8. Create the PDF.

Only JPEG (.jpeg, .jpg) photos are supported.

When an EXIF date is available, it is used to sort the photos and can optionally be displayed below each image.

## Features

* Create PDF photo contact sheets
* Automatic EXIF date detection
* Sort photos by date, ascending or descending
* Handle photos without an EXIF date
* Configurable number of rows and columns
* Optional photo dates below images
* Portrait and landscape page orientations
* Page preview before PDF generation
* Progress indicator
* GTK4 graphical interface
* French and English translations
* Automatic system language detection
* Locale-aware date and time formatting
* Application icon and desktop menu integration
* Easy installation and removal using the Debian package manager

## Releases

Released versions of PDFMyPics are available from the project's GitHub Releases.

Each release automatically produces a Debian `.deb` package.

The package is built automatically by GitHub Actions whenever a new release is published.

## Installation from source

Installing from source is mainly intended for development and testing.

PDFMyPics requires:

* Python 3.12 or newer
* GTK4
* PyGObject
* Pillow
* ReportLab

On Ubuntu or Linux Mint:

```bash
sudo apt install python3 python3-gi gir1.2-gtk-4.0 python3-pil python3-reportlab
```

Then, from the project directory:

```bash
python3 main.py
```

## Translations

PDFMyPics is currently available in:

* 🇫🇷 French
* 🇬🇧 English

The application automatically detects the system language and uses the corresponding translation when available.

Translations are handled using GNU gettext.

## License

PDFMyPics is distributed under the **GNU General Public License version 3 or later (GPL-3.0-or-later)**.

See the [LICENSE](LICENSE) file for details.

## Project status

PDFMyPics is currently under development.

Bug reports, suggestions, and contributions are welcome.
