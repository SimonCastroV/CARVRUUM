# CarVRuuum - Guía rápida para levantar el proyecto en AWS EC2

## Datos importantes

Elastic IP fija:

```text
100.50.61.211
```

URL de la página:

```text
http://100.50.61.211:8000
```

Usuario para entrar por EC2 Instance Connect:

```text
ec2-user
```

---

## 1. Entrar al servidor AWS

En AWS ir a:

```text
EC2 > Instancias > Seleccionar CarVruum > Conectar
```

Entrar por:

```text
Conexión de la instancia EC2
```

Usuario:

```text
ec2-user
```

Luego dar clic en:

```text
Conectar
```

---

## 2. Entrar a la carpeta del proyecto

Una vez dentro de la terminal de AWS:

```bash
cd CARVRUUM
```

Verificar que estás en la carpeta correcta:

```bash
ls
```

Deberías ver algo parecido a:

```text
manage.py
requirements.txt
account
cars
media
templates
```

---

## 3. Activar el entorno virtual

```bash
source .venv/bin/activate
```

Debe aparecer algo así al inicio de la terminal:

```bash
(.venv) [ec2-user@ip-... CARVRUUM]$
```

---

## 4. Actualizar el proyecto desde GitHub

Si hiciste cambios en VS Code y ya ejecutaste `git push`, en AWS ejecuta:

```bash
git pull
```

---

## 5. Aplicar migraciones

No siempre es necesario, pero es seguro correrlo:

```bash
python3.11 manage.py migrate
```

---

## 6. Levantar la página

```bash
python3.11 manage.py runserver 0.0.0.0:8000
```

Cuando salga algo parecido a:

```text
Starting development server at http://0.0.0.0:8000/
```

abrir en el navegador:

```text
http://100.50.61.211:8000
```

---

## Importante

No cerrar la terminal de AWS mientras la página esté corriendo.

Si cierras la terminal, la página se apaga porque el servidor está corriendo manualmente con:

```bash
python3.11 manage.py runserver 0.0.0.0:8000
```

Para apagar el servidor manualmente:

```bash
CTRL + C
```

Para volverlo a prender:

```bash
python3.11 manage.py runserver 0.0.0.0:8000
```

---

## Flujo normal para actualizar la página

### En VS Code local

```bash
git add .
git commit -m "Update project"
git push
```

### En AWS

```bash
cd CARVRUUM
source .venv/bin/activate
git pull
python3.11 manage.py migrate
python3.11 manage.py runserver 0.0.0.0:8000
```

---

## Si la página no carga

Revisar que en AWS esté abierto el puerto `8000`.

Ruta:

```text
EC2 > Instancias > CarVruum > Seguridad > Grupo de seguridad > Reglas de entrada
```

Debe existir una regla así:

```text
Tipo: TCP personalizado
Puerto: 8000
Origen: 0.0.0.0/0
```

---

## Configuración importante en Django

En `settings.py`, `ALLOWED_HOSTS` debe permitir la Elastic IP:

```python
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        "DJANGO_ALLOWED_HOSTS",
        "127.0.0.1,localhost,100.50.61.211"
    ).split(",")
    if host.strip()
]
```

Asegurarse de tener arriba:

```python
import os
```

---

## Nota final

Actualmente la página funciona en modo desarrollo con:

```bash
python3.11 manage.py runserver 0.0.0.0:8000
```

Más adelante lo ideal es dejarla funcionando en producción con:

```text
Gunicorn + Nginx + systemd
```

Así la página seguiría activa aunque se cierre la terminal de AWS.
