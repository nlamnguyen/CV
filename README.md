# CV — générateur statique en Python

Ce dépôt sépare le **contenu** du CV (`data/cv_data.yaml`) de sa
**présentation** (`templates/index.html.j2`, thème Orbit de 3rd Wave
Media). Un script Python (`build.py`) assemble les deux pour produire
`index.html`, le fichier servi par GitHub Pages.

Résultat : Utilisation de YAML pour mettre à jour le CV, on relance le build pour générer l'index.html.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Utilisation

```bash
# Génère index.html une fois
python build.py

# Regénère automatiquement à chaque modification de data/ ou templates/
python build.py --watch

# Vérifie s'il y a des changements sans écraser index.html (affiche un diff)
python build.py --check

# Vérifie que build.py respecte PEP8
flake8 build.py
```

## Modifier le CV

Toutes les sections (formation, langues, expériences, compétences,
réalisations…) sont dans `data/cv_data.yaml`. Il suffit d'éditer ce
fichier — pas besoin de toucher au HTML.

Exemple pour ajouter une expérience :

```yaml
experiences:
  - title: "title"
    time: "time - time"
    company: "company"
    company_href: null/URL
    assignment_title: "assignment_title"
    paragraphs:
      - "Description"
    tools: "tools"
```

## Déploiement automatique (GitHub Actions)

Le workflow `.github/workflows/build.yml` relance `build.py` et
commit automatiquement `index.html` à chaque push qui touche
`data/cv_data.yaml`, `templates/` ou `build.py`. Il faut juste que le
dépôt GitHub ait l'autorisation "Read and write permissions" pour les
Actions (Settings → Actions → General → Workflow permissions).

## Structure du projet

```
cv-generator/
├── data/
│   └── cv_data.yaml          # tout le contenu du CV
├── templates/
│   └── index.html.j2         # structure HTML (thème Orbit)
├── build.py                  # génère index.html
├── requirements.txt
└── .github/workflows/build.yml
```