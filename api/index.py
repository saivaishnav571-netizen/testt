import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
backend_dir = os.path.join(project_root, 'backend')
ml_src_dir = os.path.join(project_root, 'ml-model', 'src')

for path in [backend_dir, project_root, ml_src_dir]:
    if path not in sys.path:
        sys.path.insert(0, path)

from main import app
