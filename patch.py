from pathlib import Path
import shutil

path = Path.cwd() / 'path.txt'
with path.open() as file:
    path_to_venv = file.readline().rstrip()

path = Path(path_to_venv) / 'lib' / 'site-packages' / 'pyqtgraph'
old_file = path / 'ptime.py'
back_file = path / 'ptime_old.py'
new_file = Path.cwd() / 'extra' / 'ptime.py'

if not back_file.exists():
    old_file.rename(back_file)
    shutil.copyfile(new_file, old_file)
    print(f'путь к окружению: {path_to_venv}')
    print('Патч успешно установлен')
