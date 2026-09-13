#!/bin/bash

set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

# Read the project version from pyproject.toml
VERSION=$(sed -n 's/^version = "\(.*\)"/\1/p' pyproject.toml)

if [ -z "$VERSION" ]; then
    echo "Erreur : impossible de trouver la version dans pyproject.toml"
    exit 1
fi

echo "PDFMyPics version $VERSION"
echo "Mise à jour du catalogue de traductions..."

xgettext \
    --language=Python \
    --keyword=_ \
    --package-name="PDFMyPics" \
    --package-version="$VERSION" \
    --copyright-holder="PDFMyPics" \
    --output=locale/pdfmypics.pot \
    pdfmypics/*.py

sed -i \
    -e '/^"PO-Revision-Date:/d' \
    -e '/^"Last-Translator:/d' \
    -e '/^"Language-Team:/d' \
    -e '/^"Language:/d' \
    locale/pdfmypics.pot

sed -i \
    -e '/^# SOME DESCRIPTIVE TITLE\./d' \
    -e '/^# Copyright (C) YEAR PDFMyPics$/d' \
    -e '/^# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR\.$/d' \
    locale/pdfmypics.pot

echo "Mise à jour des traductions françaises..."
msgmerge --update \
    locale/fr/LC_MESSAGES/pdfmypics.po \
    locale/pdfmypics.pot

echo "Mise à jour des traductions anglaises..."
msgmerge --update \
    locale/en/LC_MESSAGES/pdfmypics.po \
    locale/pdfmypics.pot

echo "Compilation française..."
msgfmt \
    locale/fr/LC_MESSAGES/pdfmypics.po \
    -o locale/fr/LC_MESSAGES/pdfmypics.mo

echo "Compilation anglaise..."
msgfmt \
    locale/en/LC_MESSAGES/pdfmypics.po \
    -o locale/en/LC_MESSAGES/pdfmypics.mo

echo "Vérification..."
msgfmt --check locale/fr/LC_MESSAGES/pdfmypics.po
msgfmt --check locale/en/LC_MESSAGES/pdfmypics.po

echo "Traductions mises à jour avec succès."
