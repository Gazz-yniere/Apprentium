# Apprentium

![Version](https://img.shields.io/badge/version-1.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.6+-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

## Table des matières
- [Description](#description)
- [Fonctionnalités](#fonctionnalités)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Utilisation](#utilisation)
  - [Mode Python](#mode-python)
  - [Mode Exécutable Windows](#mode-exécutable-windows)
- [Personnalisation](#personnalisation)
- [Création de l'exécutable](#création-de-lexécutable)
- [Contribuer](#contribuer)

## Description
Apprentium est une application de bureau développée en Python avec une interface graphique conviviale (basée sur PyQt6). Elle est conçue pour aider à la création de cahiers d'exercices personnalisés pour les élèves, couvrant un large éventail de matières. L'application permet de générer ces fiches d'exercices aux formats PDF et Word.

Les utilisateurs peuvent finement ajuster les paramètres de chaque type d'exercice (nombre d'items, difficulté, options spécifiques) directement depuis l'interface. Ces configurations sont automatiquement sauvegardées dans un fichier `config.json` pour une réutilisation facile.

## Fonctionnalités

### Matières couvertes
- **Calculs** : additions, soustractions, multiplications, divisions, énumération de nombres, petits problèmes
- **Mesures** : conversions d'unités, rangement de nombres, encadrement
- **Conjugaison** : exercices adaptés par niveau
- **Grammaire** : types de phrases, transformations
- **Orthographe** : homophones
- **Anglais** : phrases à compléter, jeux de mots à relier

### Autres fonctionnalités
- Interface utilisateur intuitive avec onglets par matière
- Génération de documents aux formats PDF et Word
- Sauvegarde automatique des paramètres
- Personnalisation facile du contenu pédagogique via fichiers JSON
- Adaptation des exercices par niveau scolaire (CP, CE1, etc.)

## Prérequis
- Python 3.6 ou supérieur
- Bibliothèques requises :
  - PyQt6 (interface graphique)
  - PyQt6-WebEngine (composants web)
  - reportlab (génération de PDF)
  - python-docx (génération de documents Word)

## Installation
1. Clonez ce dépôt ou téléchargez les fichiers source
2. Installez les dépendances nécessaires avec :

```bash
pip install -r requirements.txt
```

## Utilisation

### Mode Python
1. Exécutez `Apprentium.py` pour lancer l'application :
   ```bash
   python src/Apprentium.py
   ```
2. Personnalisez les paramètres dans chaque onglet (calculs, conjugaison, grammaire, etc.)
3. Cliquez sur "Générer PDF" ou "Générer Word" pour créer la fiche d'exercices
4. Le document généré est automatiquement enregistré dans le dossier `output/`

### Mode Exécutable Windows
1. Téléchargez la version compilée ou créez l'exécutable (voir section [Création de l'exécutable](#création-de-lexécutable))
2. Lancez `Apprentium.exe` (aucune installation Python requise)
3. Configurez les exercices selon vos besoins
4. Générez les documents PDF ou Word qui seront sauvegardés dans le dossier `output/`

## Personnalisation

Le contenu pédagogique de base est stocké dans des fichiers JSON dédiés, ce qui permet une personnalisation et une extension aisées du matériel pédagogique.

### Contenu des exercices
- **Verbes** : éditez `verbes.json` pour ajouter/supprimer des verbes par groupe
- **Phrases de grammaire** : éditez `phrases_grammaire.json` pour enrichir les exercices
- **Phrases en anglais** : modifiez `phrases_anglais_complexe.json` et `phrases_anglais_simple.json`
- **Mots à relier** : personnalisez `mots_a_relier.json`
- **Homophones** : ajustez `homophones.json`
- **Petits problèmes (Maths)** : éditez `problemes_maths.json` pour ajouter ou modifier les énoncés

### Configuration par niveau
- Éditez `levels_config.json` pour définir quels types d'exercices sont disponibles pour chaque niveau scolaire (CP, CE1, etc.)

### Apparence des documents
- Modifiez ou remplacez les images dans le dossier `src/img/` (ex: calculs.png, mesures.png) pour changer les illustrations des sections dans les documents PDF générés
- Personnalisez le style CSS dans `src/css/cours_style.css` pour modifier l'apparence des documents

## Création de l'exécutable

Pour créer un exécutable Windows autonome :

1. Installez PyInstaller :
   ```bash
   pip install pyinstaller
   ```

2. Compilez l'application avec la commande suivante :
   ```bash
   pyinstaller --onefile --noconsole --icon=src/Apprentium.ico --add-data "src/json;json" --add-data "src/img;img" --add-data "src/css;css" --add-data "src/Apprentium.ico;." --add-data "src/config.json;." src/Apprentium.py
   ```

3. Dans le dossier `dist/` créé, vous trouverez :
   - `Apprentium.exe` - l'exécutable principal
   - Les dossiers et fichiers nécessaires au fonctionnement

4. Pour une distribution complète, assurez-vous d'inclure :
   - `Apprentium.exe`
   - `config.json`
   - `Apprentium.ico`
   - Le dossier `json/` avec tous les fichiers de contenu
   - Le dossier `img/` pour les illustrations des PDF
   - Le dossier `css/` pour les styles

## Contribuer

Les contributions sont les bienvenues ! Voici comment vous pouvez contribuer :

1. Forkez le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b nouvelle-fonctionnalite`)
3. Committez vos changements (`git commit -m 'Ajout d'une nouvelle fonctionnalité'`)
4. Poussez vers la branche (`git push origin nouvelle-fonctionnalite`)
5. Ouvrez une Pull Request

N'hésitez pas à proposer des améliorations ou signaler des bugs en ouvrant une issue.