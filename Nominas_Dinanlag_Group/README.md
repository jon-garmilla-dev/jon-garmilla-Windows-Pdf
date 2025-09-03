# Asistente de Envío de Nóminas

Esta es una aplicación de escritorio para procesar y enviar nóminas de forma masiva desde un archivo PDF maestro.

## Construcción del Ejecutable

Para construir el ejecutable `.exe` para Windows, es necesario tener Docker instalado. El proceso de construcción se realiza dentro de un contenedor de Docker para asegurar un entorno limpio y reproducible.

### Comando de Construcción

Ejecute el siguiente comando en la raíz del repositorio (`Nominas_Dinanlag_Group`):

```shell
cd Nominas_Dinanlag_Group && docker run --rm -v "$(pwd):/app" -w /app python:3.9 sh -c "apt-get update && apt-get install -y tk-dev binutils && pip install -r requirements.txt && python build.py"
```

### Resultado

Una vez que el comando finalice, encontrará el ejecutable `EnviarNominas.exe` dentro de la carpeta `dist/`.
