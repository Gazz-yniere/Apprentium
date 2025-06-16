# EduForge

## Description
EduForge est une application de bureau développée en Python avec une interface graphique conviviale (basée sur PyQt6). Elle est conçue pour aider à la création de cahiers d'exercices personnalisés pour les élèves, couvrant un large éventail de matières. L'application permet de générer ces fiches d'exercices aux formats PDF et Word.

Les utilisateurs peuvent finement ajuster les paramètres de chaque type d'exercice (nombre d'items, difficulté, options spécifiques) directement depuis l'interface. Ces configurations sont automatiquement sauvegardées dans un fichier `config.json` pour une réutilisation facile. Le contenu pédagogique de base, tel que les listes de verbes, les phrases pour les exercices de grammaire, les homophones, les phrases en anglais et les mots à relier, est stocké dans des fichiers JSON dédiés. Cela permet une personnalisation et une extension aisées du matériel pédagogique par l'utilisateur. Les matières couvertes incluent les calculs (additions, soustractions, multiplications, divisions, énumération de nombres), les mesures (conversions d'unités, rangement de nombres, encadrement), la conjugaison, la grammaire (types de phrases, transformations), l'orthographe (homophones) et l'anglais (phrases à compléter, jeux de mots à relier).

## Structure du projet
```
HolidayScriptGUI
├── src
│   ├── EduForge.py              # Point d'entrée de l'application (GUI)
│   ├── pdf_generator.py     # Logique de génération du PDF
│   ├── word_generator.py    # Logique de génération du Word
│   ├── grammar_generator.py # Gestion des phrases de grammaire (JSON)
│   ├── conjugation_generator.py # Gestion des verbes (JSON)
│   ├── conversion_generator.py # Gestion des conversions (JSON)
│   ├── anglais_generator.py # Gestion des phrases en anglais (JSON)
│   ├── exercise_data_builder.py # Gestion des données d'exercice (JSON)
│   ├── json                 # Données JSON éditables
│   │   ├── phrases_grammaire.json
│   │   ├── homophones.json
│   │   ├── mots_a_relier.json
│   │   ├── phrases_anglais_complexe.json
│   │   ├── phrases_anglais_simple.json
│   │   └── verbes.json
│   ├── config.json              # Configuration utilisateur sauvegardée
│   ├── EduForge.png         # Logo de l'application (fenêtre et .exe)
│   └── EduForge.ico            # Icône de l'application
├── requirements.txt         # Dépendances nécessaires
└── README.md                # Documentation du projet
```

## Installation
Installez les dépendances nécessaires avec :

```
pip install -r requirements.txt
```

## Utilisation (mode Python)
1. Exécutez `EduForge.py` pour lancer l'application :
   ```
   python src/EduForge.py
   ```
2. Personnalisez les paramètres (calculs, conjugaison, grammaire, etc.).
3. Cliquez sur "Générer PDF" ou "Générer Word" pour créer la fiche.
4. Le PDF ou le Word est enregistré dans le dossier output.

## Utilisation (exécutable Windows autonome)
1. Compilez avec PyInstaller (logo et dossier JSON à côté de l'exe) :
   ```
   pyinstaller --onefile --noconsole --icon=src/EduForge.ico --add-data "src/json;json" --add-data "src/img,img" --add-data "src/EduForge.ico;." --add-data "src/config.json;." src/EduForge.py
   ```
2. Dans le dossier `dist/`, copiez `EduForge.exe`, `config.json`, `EduForge.ico`, et le dossier `json`.
3. Lancez `EduForge.exe` sur n'importe quel PC Windows (aucune installation Python requise).
4. Les fichiers JSON sont modifiables à côté de l'exe pour personnaliser verbes et phrases.

## Personnalisation
- **Verbes** : éditez `verbes.json` pour ajouter/supprimer des verbes par groupe.
- **Phrases de grammaire** : éditez `phrases_grammaire.json` pour enrichir les exercices.
- **Phrases en anglais** : éditez `phrases_anglais_complexe.json` et `phrases_anglais_simple.json`
- **mots à relier** : éditez `mots_a_relier.json`
- **homophones** : éditez `homophones.json`
- **Logo** : remplacez `EduForge.png` pour changer l'icône de la fenêtre et de l'exécutable.

## Contribuer
Les contributions sont les bienvenues ! N'hésitez pas à proposer des améliorations ou signaler des bugs.