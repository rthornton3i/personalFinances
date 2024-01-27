python -m venv .venv
call .venv/Scripts/activate.bat
python -m pip install --upgrade -r _setup/requirements.pip.txt
pip install -r _setup/requirements.txt
pause