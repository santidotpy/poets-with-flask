#command -v python3 >/dev/null 2>&1 || { echo >&2 "python3 is not installed.  Aborting."; exit 1; } #Verificar si existe el comando (Válido para Ubuntu)
#dpkg-query -l python3-venv > /dev/null 2>&1 || { echo >&2 "python3-venv is not installed. Aborting.";exit 1;} #Verificar si el paquete está instalado(Válido para Ubuntu)
python3 -m venv .
source bin/activate
pip install --upgrade pip
pip3 install -r requirements.txt
