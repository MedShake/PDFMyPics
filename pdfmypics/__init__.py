from pathlib import Path
import tomllib


pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"

with pyproject.open("rb") as fichier:
    configuration = tomllib.load(fichier)

__version__ = configuration["project"]["version"]
