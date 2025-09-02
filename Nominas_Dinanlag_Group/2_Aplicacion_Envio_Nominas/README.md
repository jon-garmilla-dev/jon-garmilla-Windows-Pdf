# 2. Aplicación de Envío de Nóminas

Esta es la herramienta principal para automatizar el proceso de envío de nóminas.

## Flujo de Trabajo

1.  **Colocar el PDF maestro** de la gestoría en la carpeta `1_pdf_maestro_entrada/`.
2.  **Asegurarse de que el archivo `lista_empleados.csv`** en la carpeta `3_datos_empleados/` está actualizado con los NIFs, nombres y emails correctos.
3.  **Configurar las credenciales** de email en el archivo `config.py`.
4.  **Ejecutar el script `EnviarNominas.py`**.

El script procesará el PDF, dividirá cada nómina, la encriptará con el NIF del empleado y la enviará al correo correspondiente.
