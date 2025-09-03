# Gestor de Nóminas

Aplicación de escritorio profesional para procesar y enviar nóminas de forma masiva y segura.

## Características Principales

- **Procesamiento masivo**: Gestiona múltiples empleados simultáneamente
- **Validación automática**: Verifica datos antes del envío
- **Envío seguro**: Encriptación de PDFs con contraseñas personalizadas
- **Interfaz intuitiva**: Diseño paso a paso para facilitar el uso
- **Respaldo automático**: Backup antes de realizar cambios
- **Informes detallados**: Seguimiento completo del proceso de envío

## Requisitos del Sistema

### Software Necesario
- Python 3.9 o superior
- Tkinter (incluido en la mayoría de instalaciones Python)
- Dependencias especificadas en `requirements.txt`

### Sistemas Operativos Soportados
- Windows 10/11
- macOS 10.14+
- Linux (Ubuntu, Debian, CentOS, etc.)

## Instalación

1. **Clonar el repositorio**
   ```bash
   git clone [URL_DEL_REPOSITORIO]
   cd Pdf-Manipulation-Test
   ```

2. **Crear entorno virtual** (recomendado)
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # o
   venv\Scripts\activate     # Windows
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar la aplicación**
   ```bash
   python sistema_nominas/main.py
   ```

## Uso de la Aplicación

### Paso 1: Selección de Archivos
- Seleccione el archivo PDF maestro con las nóminas
- Elija el archivo Excel/CSV con los datos de empleados
- Configure el mapeo de columnas (automático en la mayoría de casos)

### Paso 2: Verificación de Datos
- Revise la lista de empleados y sus datos
- Corrija cualquier error detectado automáticamente
- Valide que toda la información está completa

### Paso 3: Envío de Correos
- Configure los parámetros de correo electrónico
- Revise la configuración antes del envío
- Inicie el proceso de envío masivo

## Configuración

La aplicación utiliza un archivo `settings.ini` para almacenar:
- Configuración de servidor de correo
- Últimos archivos utilizados
- Preferencias de usuario

## Estructura del Proyecto

```
sistema_nominas/
├── main.py              # Punto de entrada de la aplicación
├── logic/               # Lógica de negocio
│   ├── file_handler.py  # Manejo de archivos
│   ├── email_sender.py  # Envío de correos
│   └── settings.py      # Configuración
├── ui/                  # Interfaz de usuario
│   ├── main_window.py   # Ventana principal
│   ├── paso1.py         # Selección de archivos
│   ├── paso2.py         # Verificación
│   └── paso3.py         # Envío
└── employee_data/       # Datos de ejemplo y utilidades
```

## Solución de Problemas

### Error: "ModuleNotFoundError"
Asegúrese de que todas las dependencias estén instaladas:
```bash
pip install -r requirements.txt
```

### Error: "tkinter no encontrado"
En Linux, instale tkinter:
```bash
sudo apt-get install python3-tk
```

### Problemas con PDFs
Verifique que PyMuPDF esté correctamente instalado:
```bash
pip install pymupdf
```

## Diagnóstico del Sistema

Use el script de diagnóstico para verificar la configuración:
```bash
python sistema_nominas/diagnostico.py
```

## Seguridad

- Los PDFs se encriptan antes del envío
- Las contraseñas se generan de forma segura
- No se almacenan credenciales en texto plano
- Logs detallados para auditoría

## Soporte

Para reportar problemas o solicitar nuevas funcionalidades, consulte la documentación técnica en `sistema_nominas/README.md` o contacte al administrador del sistema.

## Licencia

Este proyecto es de uso interno. Todos los derechos reservados.