import sys
import os

def get_project_root():
    """
    Retourne le dossier racine pour les accès fichiers :
    - En mode PyInstaller : dossier du .exe
    - En mode dev : dossier src/ qui contient tous les .py
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller : toujours le dossier du .exe
        return os.path.dirname(sys.executable)
    else:
        # Mode dev : on cherche le dossier src/ qui contient tous les .py
        cur = os.path.dirname(os.path.abspath(__file__))  # on est dans src/utils/
        return os.path.dirname(cur)  # on remonte à src/

def project_file_path(rel_path):
    """
    Retourne le chemin absolu d'un fichier/dossier à partir de la racine (voir get_project_root).
    rel_path : chemin relatif depuis src/ (ex: 'json/xxx.json' ou 'html/data/images/xxx.png')
    """
    root = get_project_root()
    abs_path = os.path.abspath(os.path.join(root, rel_path))
    # Crée le dossier parent si besoin (pour écriture)
    parent_dir = os.path.dirname(abs_path)
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)
    return abs_path
