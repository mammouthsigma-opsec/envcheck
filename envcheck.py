#!/usr/bin/env python3
"""Compare les variables déclarées dans un fichier .env avec un exemple."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _strip_inline_comment(value: str) -> str:
    """Retire un commentaire non cité, introduit par un # précédé d'espaces."""
    quote: str | None = None
    escaped = False
    for index, char in enumerate(value):
        if escaped:
            escaped = False
            continue
        if char == "\\" and quote == '"':
            escaped = True
            continue
        if quote:
            if char == quote:
                quote = None
        elif char in ("'", '"'):
            quote = char
        elif char == "#" and (index == 0 or value[index - 1].isspace()):
            return value[:index].rstrip()
    return value.rstrip()


def parse_env(content: str) -> dict[str, str]:
    """Parse un sous-ensemble courant des fichiers dotenv en dictionnaire."""
    variables: dict[str, str] = {}
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            continue
        key, raw_value = line.split("=", 1)
        key = key.strip()
        if not key:
            continue
        value = raw_value.strip()
        if value.startswith(('"', "'")):
            quote = value[0]
            closing = value.find(quote, 1)
            if closing >= 0:
                parsed = value[1:closing]
            else:
                parsed = value[1:]
            value = parsed
        else:
            value = _strip_inline_comment(value)
        variables[key] = value
    return variables


def check_files(env_path: Path, example_path: Path, strict: bool = False) -> int:
    """Affiche les écarts entre les fichiers et renvoie le code de sortie CLI."""
    try:
        env_vars = parse_env(env_path.read_text(encoding="utf-8"))
        example_vars = parse_env(example_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        print(f"❌ Fichier introuvable : {exc.filename}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"❌ Impossible de lire un fichier : {exc}", file=sys.stderr)
        return 2

    missing = sorted(example_vars.keys() - env_vars.keys())
    extra = sorted(env_vars.keys() - example_vars.keys())
    empty = sorted(key for key in example_vars.keys() & env_vars.keys() if not env_vars[key].strip()) if strict else []

    for key in missing:
        print(f"❌ Variable manquante : {key}")
    for key in extra:
        print(f"⚠️ Variable en trop : {key}")
    for key in empty:
        print(f"❌ Variable vide : {key}")

    if missing or empty:
        return 1
    print("✅ Toutes les variables requises sont présentes" + (" et non vides" if strict else "") + ".")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compare les variables d'un fichier .env avec .env.example."
    )
    parser.add_argument("--env", default=".env", help="fichier .env à vérifier (défaut : .env)")
    parser.add_argument("--example", default=".env.example", help="fichier modèle (défaut : .env.example)")
    parser.add_argument("--strict", action="store_true", help="échoue aussi si une variable requise est vide")
    args = parser.parse_args(argv)
    return check_files(Path(args.env), Path(args.example), args.strict)


if __name__ == "__main__":
    raise SystemExit(main())
