# Image qui va être créer
FROM python:latest 

# Copy le fichier requirements vers le fichier /usr/src/app/
COPY requirements.txt /usr/src/app/

# Excécute le requirement
RUN pip3 install -r /usr/src/app/requirements.txt

# Copy tout le contenu du fichier excécutable du workin dir sur dans le docker
COPY . /usr/src/app

# Créer le dossier dans le conteneur
WORKDIR /usr/src/app

# Utilise le port 5000
EXPOSE 5000

# Excécute le programme
ENTRYPOINT ["python3", "main.py"]

# docker build -t bot-test .
# docker run bot-test