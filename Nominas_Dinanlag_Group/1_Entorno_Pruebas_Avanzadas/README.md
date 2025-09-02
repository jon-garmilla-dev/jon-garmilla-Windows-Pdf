# 1. Entorno de Pruebas Avanzadas

Este módulo se utiliza para generar datos de prueba masivos.

## Flujo de Trabajo

1.  **`preparar_plantilla.py`**: Convierte un PDF de nómina real y protegido en una plantilla limpia con un placeholder (`XXXXXXXXL`) para el NIF.
2.  **`generador.py`**: Usa la plantilla para crear un único PDF maestro con 50 nóminas falsas y un CSV con los datos de los empleados.
3.  **`divisor.py`**: Divide el PDF maestro en 50 archivos individuales como prueba de concepto.
