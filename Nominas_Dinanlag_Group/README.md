# 📧 Asistente de Envío de Nóminas v2.0

**Aplicación de escritorio profesional para procesar y enviar nóminas de forma masiva y segura.**

## 🌟 Características Principales

- ✅ **Interfaz gráfica intuitiva** estilo Windows clásico
- 🔐 **Credenciales cifradas automáticamente** para máxima seguridad  
- 👁️ **Previsualizador de PDFs** integrado para verificación visual
- 🛠️ **Corrección manual** de datos con validación inteligente
- 📊 **Estadísticas en tiempo real** del proceso de envío
- 🎯 **Diseñado para usuarios no técnicos** con ayuda contextual

## 📋 Requisitos del Sistema

- **Sistema Operativo**: Windows 10/11, macOS, o Linux
- **Python**: 3.9 o superior (solo para desarrollo)
- **Memoria RAM**: 4GB mínimo recomendado
- **Espacio en disco**: 100MB para la aplicación + espacio para PDFs

## 🚀 Instalación y Uso

### Opción A: Ejecutable (Recomendado)
1. Descargue `EnviarNominas.exe` de la carpeta `dist/`
2. Ejecute el archivo directamente
3. La aplicación se abrirá automáticamente

### Opción B: Desde Código Fuente
```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar aplicación
cd sistema_nominas
python main.py
```

## 📖 Guía Rápida de Uso

### 1️⃣ **Configuración Inicial**
- Al abrir por primera vez, vaya a **"Configuración"**
- Configure su email y contraseña de aplicación
- Configure la contraseña de edición de PDFs
- ¡Las credenciales se cifran automáticamente!

### 2️⃣ **Paso 1: Selección de Archivos**
- **PDF de Nóminas**: Archivo con todas las nóminas
- **Datos de Empleados**: Archivo Excel/CSV con NIF, nombres y emails
- La aplicación detecta automáticamente las columnas

### 3️⃣ **Paso 2: Verificación**
- Revise los datos extraídos automáticamente
- ✅ Verde = Listo para envío
- ❌ Rojo = Requiere corrección
- **Doble clic** para corregir con previsualizador

### 4️⃣ **Paso 3: Envío**
- Confirme el envío masivo
- Vea el progreso en tiempo real
- Estadísticas finales al completar

## 🔧 Construcción del Ejecutable

Para crear un nuevo ejecutable desde el código:

```bash
# Usando Docker (recomendado para consistencia)
cd Nominas_Dinanlag_Group
docker run --rm -v "$(pwd):/app" -w /app python:3.9 sh -c "apt-get update && apt-get install -y tk-dev binutils && pip install -r requirements.txt && python build.py"

# O localmente si tiene Python configurado
pip install -r requirements.txt
python build.py
```

El ejecutable se generará en `dist/EnviarNominas.exe`

## 📁 Estructura del Proyecto

```
Nominas_Dinanlag_Group/
├── sistema_nominas/               # Aplicación principal
│   ├── main.py                     # Punto de entrada
│   ├── ui/                         # Interfaz gráfica
│   │   ├── main_window.py          # Ventana principal
│   │   ├── paso1.py               # Selección archivos
│   │   ├── paso2.py               # Verificación + Preview
│   │   ├── paso3.py               # Envío
│   │   ├── paso_ajustes.py        # Configuración
│   │   └── paso_completado.py     # Resumen final
│   └── logic/                      # Lógica de negocio
│       ├── email_sender.py         # Envío de correos
│       ├── file_handler.py         # Procesamiento archivos
│       ├── settings.py             # Configuración
│       └── security.py             # Cifrado credenciales
├── development_tools/             # Herramientas de desarrollo y testing
├── requirements.txt                # Dependencias
├── build.py                       # Script construcción
├── SECURITY.md                    # Documentación seguridad
└── README.md                      # Este archivo
```

## 🔒 Seguridad

- **Credenciales cifradas** con clave única por instalación
- **Contraseñas de PDFs** protegidas automáticamente  
- **Backup automático** de configuración
- **Sin exposición de datos** en logs o archivos temporales

Ver [SECURITY.md](SECURITY.md) para más detalles.

## 🆘 Solución de Problemas

### "Error al enviar correos"
- Verifique su conexión a internet
- Confirme que el email y contraseña son correctos
- Para Gmail, use contraseña de aplicación

### "No se puede abrir PDF"
- Verifique que el archivo no esté corrupto
- Asegúrese de tener permisos de lectura
- Use "Ver PDF Completo" para diagnosticar

### "Datos no encontrados"
- Revise que las columnas estén bien asignadas
- Verifique formato del archivo de empleados
- Use el botón "Volver a Verificar"

## 👥 Para Equipos IT

- **Logging**: Los logs se almacenan automáticamente
- **Configuración centralizada**: Archivo `settings.ini` cifrado
- **Deployment**: Ejecutable portátil sin instalación
- **Backup**: Sistema automático de respaldo de configuración

## 📞 Soporte

Para problemas técnicos o consultas:
- Consulte la documentación en cada pantalla
- Use el botón "¿Necesita Ayuda?" en la aplicación
- Revise los archivos de configuración en caso de errores

---

**Versión:** 2.0  
**Última actualización:** Septiembre 2025  
**Compatibilidad:** Windows, macOS, Linux