python -m venv .venv
call .venv/Scripts/activate.bat
call python -m pip install --upgrade -r _setup/requirements.pip.txt
call pip install -r _setup/requirements.txt