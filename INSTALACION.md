# 🚀 Guía de Instalación y Deployment

**Para administradores IT y desarrolladores**

---

## 📊 Para Usuarios Finales (Secretarias/Admin)

### ✅ Instalación Rápida (Recomendada)

1. **Descargar**: Obtener `EnviarNominas.exe` de la carpeta `dist/`
2. **Ejecutar**: Doble clic en el archivo - ¡NO necesita instalación!
3. **Configurar**: La primera vez, configurar email en "Configuración"
4. **¡Listo!**: Comenzar a usar inmediatamente

### 📋 Requisitos del Usuario Final
- **SO**: Windows 10/11 (recomendado) o Windows 8.1+
- **RAM**: 4GB mínimo
- **Espacio**: 100MB para la app + espacio para PDFs temporales
- **Red**: Conexión a internet para envío de emails
- **Email**: Cuenta de email con SMTP configurado (Gmail, Outlook, etc.)

---

## 🛠️ Para Desarrolladores

### 🏗️ Configuración del Entorno de Desarrollo

#### 1. Clonar Repositorio
```bash
git clone <url-repositorio>
cd Nominas_Dinanlag_Group
```

#### 2. Instalar Python
- **Python 3.9+** (recomendado 3.11)
- Verificar: `python --version`

#### 3. Crear Entorno Virtual (Recomendado)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux  
python -m venv venv
source venv/bin/activate
```

#### 4. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 📦 Dependencias Principales
```
# GUI y sistema
tkinter (incluido con Python)

# Procesamiento PDFs
pymupdf          # Lectura y manipulación PDFs
pikepdf          # Encriptación PDFs

# Datos y archivos  
pandas           # Análisis datos empleados
openpyxl         # Soporte Excel

# Imágenes (opcional)
Pillow           # Previsualizador PDFs

# Seguridad
cryptography     # Cifrado credenciales

# Testing y generación datos
Faker            # Solo para entorno de pruebas

# Empaquetado
pyinstaller      # Generar ejecutables
```

### 🧪 Testing Local
```bash
cd sistema_nominas
python main.py
```

**Verificaciones básicas:**
- ✅ La ventana se abre correctamente
- ✅ Se pueden seleccionar archivos
- ✅ El cifrado funciona (crear configuración)
- ✅ La navegación entre pasos funciona

---

## 📦 Generación de Ejecutables

### 🐳 Método Docker (Recomendado)

**Ventajas**: Entorno limpio, reproducible, cross-platform

```bash
cd Nominas_Dinanlag_Group

# Generar ejecutable para Windows
docker run --rm -v "$(pwd):/app" -w /app python:3.9 sh -c "apt-get update && apt-get install -y tk-dev binutils && pip install -r requirements.txt && python build.py"
```

**Resultado**: `dist/EnviarNominas.exe` (o `EnviarNominas` en Linux)

### 🏠 Método Local

```bash
# 1. Instalar dependencias localmente
pip install -r requirements.txt

# 2. Ejecutar script de build
python build.py

# 3. Probar ejecutable
dist/EnviarNominas.exe
```

### 🔧 Personalizar Build

Modificar `build.py`:

```python
pyinstaller_args = [
    script_path,
    '--onefile',              # Un solo archivo
    '--name', NOMBRE_EXE,     # Nombre del ejecutable
    '--clean',                # Limpiar cache anterior
    '--noconfirm',           # No pedir confirmaciones
    # '--windowed',           # Sin consola (descomentar para prod)
    # '--icon=icon.ico',      # Icono personalizado
]
```

---

## 🏢 Deployment Empresarial

### 📁 Estructura de Deployment
```
deployment/
├── EnviarNominas.exe           # Aplicación principal
├── MANUAL_USUARIO.md           # Manual para usuarios
├── INSTALACION.md              # Este archivo
├── configuracion/
│   └── settings_template.ini   # Plantilla configuración
└── docs/
    └── troubleshooting.md      # Solución problemas
```

### 🎯 Opciones de Distribución

#### Opción A: Archivo Individual
- **Ventajas**: Portátil, sin instalación
- **Distribución**: Copiar `EnviarNominas.exe` via USB, red, email
- **Configuración**: Cada usuario configura individualmente

#### Opción B: MSI Installer (Avanzado)
```bash
# Usar herramientas como Advanced Installer o Inno Setup
# Incluir:
# - Ejecutable principal
# - Documentación
# - Configuración por defecto
# - Acceso directo en escritorio
```

#### Opción C: Configuración Centralizada
```ini
# Pre-configurar settings_template.ini
[SMTP]
servidor = smtp.empresa.com
puerto = 587

[Carpetas] 
salida = \\servidor\nominas\salida\
```

### 🔐 Consideraciones de Seguridad

#### Para IT/Administradores
- ✅ **Antivirus**: Añadir exclusión para `EnviarNominas.exe`
- ✅ **Firewall**: Permitir conexiones SMTP (puerto 587/465)
- ✅ **Permisos**: Usuarios necesitan escribir en carpeta de salida
- ✅ **Backup**: Respaldar carpeta de configuración regularmente

#### Configuración Email Empresarial
```ini
# Gmail con contraseñas de aplicación
[SMTP]
servidor = smtp.gmail.com
puerto = 587

# Outlook 365
[SMTP]  
servidor = smtp-mail.outlook.com
puerto = 587

# Exchange Server local
[SMTP]
servidor = mail.empresa.local
puerto = 25
```

---

## 🐛 Troubleshooting Deployment

### Errores Comunes Build

#### "ModuleNotFoundError: No module named 'tkinter'"
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# CentOS/RHEL  
sudo yum install tkinter
```

#### "Permission denied" en Docker
```bash
# Linux: Dar permisos al usuario
sudo usermod -a -G docker $USER
logout && login

# Windows: Ejecutar PowerShell como administrador
```

#### Ejecutable muy grande (>100MB)
```python
# En build.py, añadir optimizaciones:
'--exclude-module=matplotlib',
'--exclude-module=numpy.distutils',
'--optimize=2'
```

### Errores Comunes Deployment

#### "Aplicación no abre en PC destino"
- ✅ Verificar arquitectura (32-bit vs 64-bit)
- ✅ Instalar Visual C++ Redistributables
- ✅ Verificar permisos de ejecución

#### "No puede escribir archivos"
- ✅ Ejecutar como administrador primera vez
- ✅ Verificar permisos carpeta de salida
- ✅ Configurar carpeta de salida en ubicación accesible

#### "Error de conexión SMTP"  
- ✅ Verificar firewall corporativo
- ✅ Comprobar configuración proxy
- ✅ Validar credenciales email

---

## 📊 Monitoreo y Mantenimiento

### 🔍 Logs para IT
```python
# Los logs aparecen en consola cuando se ejecuta desde terminal
# Para capturar en archivo:
python main.py > logs/nominas.log 2>&1
```

### 📈 KPIs para Tracking
- ✅ **Tiempo promedio** por envío de lote
- ✅ **Tasa de éxito** de envíos
- ✅ **Errores comunes** por usuario
- ✅ **Volumen de nóminas** procesadas

### 🔄 Actualizaciones
1. **Desarrollo**: Modificar código y probar
2. **Build**: Generar nuevo ejecutable
3. **Testing**: Probar con datos reales en entorno controlado
4. **Deployment**: Reemplazar ejecutable en producción
5. **Comunicación**: Notificar cambios a usuarios

---

## 📞 Soporte IT

### Información para Tickets
Al reportar problemas, incluir:
- ✅ **Versión**: Del ejecutable
- ✅ **SO**: Windows version y arquitectura  
- ✅ **Error**: Mensaje exacto y captura pantalla
- ✅ **Contexto**: Qué estaba haciendo el usuario
- ✅ **Archivos**: Logs relevantes

### Escalación
1. **Nivel 1**: Problemas de configuración usuario
2. **Nivel 2**: Errores de conectividad/permisos  
3. **Nivel 3**: Bugs en código o mejoras funcionales

---

**¡Deployment exitoso significa usuarios productivos! 🎉**