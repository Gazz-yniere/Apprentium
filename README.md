# Apprentium

![Version](https://img.shields.io/badge/version-0.25.7a-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10+-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

## Table des matières
- [Description détaillée](#description-détaillée)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Personnalisation](#personnalisation)
- [Création de l'exécutable Windows](#création-de-lexécutable-windows)
- [Contribuer](#contribuer)
- [Bonnes pratiques et maintenance](#bonnes-pratiques-et-maintenance)

## Description détaillée

**Apprentium** est un générateur de cahiers d'exercices scolaires ultra-flexible pour le primaire (CP à CM2). Il permet de créer en quelques clics des fiches PDF ou Word entièrement personnalisées, prêtes à imprimer, adaptées au niveau et aux besoins de chaque élève ou groupe. L'application propose une interface moderne, intuitive et puissante, pensée pour les enseignants, AESH, parents ou orthophonistes.

### Ce que fait le logiciel
- Génère des fiches d'exercices sur-mesure en **maths** (calculs, problèmes, mesures), **français** (conjugaison, grammaire, orthographe) et **anglais** (phrases à compléter, mots à relier).
- Permet de choisir précisément le nombre, la difficulté, le type et la présentation de chaque exercice.
- Offre un **éditeur de cours intégré** (WYSIWYG) pour créer ou modifier des leçons, insérer des images, tableaux, listes, etc. (avec gestion avancée des images locales).
- Gère la sauvegarde automatique de tous les réglages, le rappel des derniers paramètres, et la personnalisation fine de l'apparence (dark mode, couleurs, styles, etc.).
- Génère des documents PDF/Word propres, harmonisés, avec gestion intelligente des sauts de page, cadres, images et titres.
- Permet d'ajouter, modifier ou supprimer ses propres contenus pédagogiques (verbes, phrases, problèmes, etc.) via de simples fichiers JSON.

### Options et possibilités principales
- **Sélection du niveau** : CP, CE1, CE2, CM1, CM2 (adaptation automatique des exercices proposés)
- **Personnalisation fine** : nombre d'exercices, types d'opérations, thèmes, options avancées (décimaux, négatifs, multi-opérandes, etc.)
- **Gestion des images** : upload local, insertion dans les cours, affichage garanti dans l'éditeur ET dans les PDF/Word
- **Choix du dossier de sortie** : possibilité de définir où seront enregistrés les fichiers générés
- **Sauvegarde/restauration automatique** de tous les paramètres (niveau, quantités, options, apparence, etc.)
- **Édition des cours** : création, modification, suppression de leçons pour chaque matière et chaque niveau
- **Support multi-utilisateur** : chaque utilisateur retrouve ses réglages et contenus
- **Mode sombre natif** : interface agréable et lisible, même en classe ou sur vidéoprojecteur
- **Notifications et popups** : retour utilisateur clair (erreurs, confirmations, etc.)

## Prérequis
- Python 3.10 ou supérieur
- Dépendances principales :
  - PyQt6
  - PyQt6-WebEngine
  - reportlab
  - python-docx
  - (voir `requirements.txt` pour la liste complète)

## Installation
1. Clonez ce dépôt ou téléchargez les sources
2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

## Utilisation

### 1. En mode code source (Python)

1. Installez Python 3.10+ et les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
2. Lancez l'application :
   ```bash
   python src/Apprentium.py
   ```
3. Utilisez l'interface graphique :
   - Choisissez le niveau et configurez chaque type d'exercice dans les onglets.
   - Modifiez ou créez vos propres cours dans l'éditeur intégré (onglet "Cours").
   - Cliquez sur "Générer PDF" ou "Générer Word" pour créer votre fiche.
   - Le fichier est enregistré dans le dossier de sortie choisi (par défaut `output/`).
   - Tous vos réglages sont sauvegardés automatiquement.

### 2. En mode exécutable Windows (compilé)

1. Téléchargez ou compilez l'exécutable (`Apprentium.exe`).
2. Double-cliquez sur `Apprentium.exe` (aucune installation Python requise).
3. L'interface et les options sont identiques au mode source.
4. Les fichiers générés, les images uploadées et les réglages sont stockés à côté de l'exécutable (ou dans le dossier choisi).
5. Vous pouvez distribuer le dossier à d'autres utilisateurs sans dépendances.

### Points importants (tous modes)
- **Aucune donnée n'est envoyée sur Internet** : tout reste en local.
- **Les images insérées dans les cours** sont toujours accessibles dans les PDF/Word générés.
- **Vous pouvez modifier les fichiers JSON** dans `src/json/` pour enrichir les exercices proposés.
- **Le logiciel est portable** : copiez le dossier ou l'exécutable où vous voulez, tout fonctionnera.

## Exemples d'utilisation

- Générer une fiche de calculs pour un élève de CE2 avec 10 additions, 5 soustractions et 2 problèmes.
- Créer un cours d'anglais avec images et exercices personnalisés, puis l'imprimer pour la classe.
- Adapter rapidement les exercices pour un élève en difficulté ou en avance.
- Sauvegarder et réutiliser vos propres modèles de fiches et de cours.

Pour toute question ou suggestion, consultez la section "Support et contact" ci-dessous.

## Personnalisation

### Contenu pédagogique
- **Verbes** : éditez `src/json/verbes.json` pour ajouter/supprimer des verbes
- **Phrases de grammaire** : éditez `src/json/phrases_grammaire.json`
- **Phrases en anglais** : modifiez `src/json/phrases_anglais_complexe.json` et `src/json/phrases_anglais_simple.json`
- **Mots à relier** : personnalisez `src/json/mots_a_relier.json`
- **Homophones** : ajustez `src/json/homophones.json`
- **Petits problèmes (Maths)** : éditez `src/json/problemes_maths.json`

### Configuration par niveau
- Modifiez `src/levels_config.json` pour définir les exercices disponibles par niveau

### Apparence des documents
- Modifiez/remplacez les images dans `src/img/` (ex: calculs.png, mesures.png)
- Personnalisez le style CSS dans `src/css/cours_style.css`

## Création de l'exécutable Windows

1. Installez PyInstaller :
   ```bash
   pip install pyinstaller
   ```
2. Compilez l'application avec toutes les ressources nécessaires :
   ```bash
   pyinstaller --onefile --noconsole --icon=src/Apprentium.ico --add-data "src/json;json" --add-data "src/img;img" --add-data "src/css;css" --add-data "src/html;html" --add-data "src/js;js" --add-data "src/font;font" --add-data "src/Apprentium.ico;." --add-data "src/config.json;." src/Apprentium.py
   ```
   > **Remarque** : Sur Windows, remplacez les `/` par `\` si besoin. Sur Mac/Linux, adaptez la syntaxe des chemins.
3. Dans le dossier `dist/`, vous trouverez :
   - `Apprentium.exe` (exécutable principal)
   - Tous les dossiers/fichiers nécessaires au fonctionnement
4. Pour distribuer, incluez :
   - `Apprentium.exe`
   - `config.json`
   - `Apprentium.ico`
   - Le dossier `json/` (contenu pédagogique)
   - Le dossier `img/` (illustrations)
   - Le dossier `css/` (styles)
   - Le dossier `html/` (templates HTML)
   - Le dossier `js/` (scripts JS)
   - Le dossier `font/` (polices Summernote)

## Contribuer

Les contributions sont les bienvenues !

1. Forkez le projet
2. Créez une branche (`git checkout -b nouvelle-fonctionnalite`)
3. Committez vos changements (`git commit -m 'Ajout d'une fonctionnalité'`)
4. Poussez (`git push origin nouvelle-fonctionnalite`)
5. Ouvrez une Pull Request

N'hésitez pas à proposer des améliorations ou signaler des bugs via les issues.
