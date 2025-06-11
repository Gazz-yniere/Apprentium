# HolidayScript GUI

## Description
HolidayScript GUI est une application Python permettant de générer des fiches PDF d'exercices pour élèves (calculs, conjugaison, grammaire) avec une interface graphique conviviale. Les paramètres (types d'exercices, quantités, groupes, temps, etc.) sont personnalisables et sauvegardés automatiquement. Les listes de verbes et de phrases sont éditables via des fichiers JSON à côté du programme.

## Structure du projet
```
HolidayScriptGUI
├── src
│   ├── main.py              # Point d'entrée de l'application (GUI)
│   ├── pdf_generator.py     # Logique de génération du PDF
│   ├── grammar_generator.py # Gestion des phrases de grammaire (JSON)
│   ├── conjugation_generator.py # Gestion des verbes (JSON)
│   ├── phrases_grammaire.json   # Phrases de grammaire éditables
│   ├── verbes.json              # Verbes éditables
│   ├── config.json              # Configuration utilisateur sauvegardée
│   └── logo-inv.png         # Logo de l'application (fenêtre et .exe)
├── requirements.txt         # Dépendances nécessaires
└── README.md                # Documentation du projet
```

## Installation
Installez les dépendances nécessaires avec :

```
pip install -r requirements.txt
```

## Utilisation (mode Python)
1. Exécutez `main.py` pour lancer l'application :
   ```
   python src/main.py
   ```
2. Personnalisez les paramètres (calculs, conjugaison, grammaire, etc.).
3. Cliquez sur "Générer PDF" pour créer la fiche.
4. Le PDF est enregistré dans le dossier courant.

## Utilisation (exécutable Windows autonome)
1. Compilez avec PyInstaller (logo et fichiers JSON à côté de l'exe) :
   ```
   pyinstaller --onefile --noconsole --icon=logo-inv.png --add-data "phrases_grammaire.json;." --add-data "verbes.json;." --add-data "config.json;." main.py
   ```
2. Dans le dossier `dist/`, copiez `main.exe`, `phrases_grammaire.json`, `verbes.json`, `config.json` et `logo-inv.png`.
3. Lancez `main.exe` sur n'importe quel PC Windows (aucune installation Python requise).
4. Les fichiers JSON sont modifiables à côté de l'exe pour personnaliser verbes et phrases.

## Personnalisation
- **Verbes** : éditez `verbes.json` pour ajouter/supprimer des verbes par groupe.
- **Phrases de grammaire** : éditez `phrases_grammaire.json` pour enrichir les exercices.
- **Logo** : remplacez `logo-inv.png` pour changer l'icône de la fenêtre et de l'exécutable.

## Contribuer
Les contributions sont les bienvenues ! N'hésitez pas à proposer des améliorations ou signaler des bugs.