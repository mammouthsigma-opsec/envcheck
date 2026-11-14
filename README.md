# envcheck

`envcheck` est un petit outil en ligne de commande, sans dépendance, qui compare les noms de variables présents dans votre fichier `.env` à ceux de `.env.example`. Il signale les variables manquantes et les variables supplémentaires. En mode strict, il échoue également si une variable requise est vide.

## Prérequis et installation

Python 3.9 ou plus récent est requis. Aucun paquet externe n'est nécessaire : clonez le dépôt ou téléchargez `envcheck.py`.

```bash
git clone https://github.com/mammouthsigma-opsec/envcheck.git
cd envcheck
```

## Utilisation

```bash
python envcheck.py
python envcheck.py --env .env.local --example .env.example
python envcheck.py --strict
```

Par défaut, le programme lit `.env` et `.env.example` dans le répertoire courant. Les commentaires et lignes vides sont ignorés; le préfixe `export ` et les valeurs entre guillemets simples ou doubles sont acceptés.

Exemple de réussite :

```text
✅ Toutes les variables requises sont présentes.
```

Exemple avec écart :

```text
❌ Variable manquante : DATABASE_URL
⚠️ Variable en trop : DEBUG
```

En mode strict, une variable déclarée mais vide est indiquée, par exemple `❌ Variable vide : API_KEY`.

Codes de sortie : `0` si les variables requises sont présentes (les variables en trop sont des avertissements), `1` si une variable manque ou si une variable requise est vide en mode strict, `2` si un fichier ne peut pas être trouvé ou lu.

## CI et pre-commit

Le workflow GitHub Actions du dépôt exécute les tests avec Python 3.9 à 3.12. Pour vérifier localement :

```bash
python -m pip install pytest
pytest -q
```

Vous pouvez aussi utiliser l'outil dans un hook pre-commit local : ajoutez ce bloc à `.pre-commit-config.yaml`, adaptez les chemins si nécessaire, puis exécutez `pre-commit run --all-files`.

```yaml
repos:
  - repo: local
    hooks:
      - id: envcheck
        name: Vérifier les variables .env
        entry: python envcheck.py --strict
        language: system
        pass_filenames: false
        always_run: true
```

Le fichier `.env` contient souvent des secrets : ne le commitez pas. Le dépôt ignore `.env` par défaut.

## Licence

Distribué sous licence MIT. Consultez [`LICENSE`](LICENSE).
