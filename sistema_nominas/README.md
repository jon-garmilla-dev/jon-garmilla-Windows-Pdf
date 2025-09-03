# 📧 Aplicación de Envío de Nóminas - Guía Técnica

Esta es la aplicación principal con interfaz gráfica para automatizar el proceso de envío de nóminas.

## 🏗️ Arquitectura

### Estructura de Archivos
```
sistema_nominas/
├── main.py                 # Punto de entrada principal
├── ui/                     # Interfaz de usuario
│   ├── main_window.py      # Ventana principal y navegación
│   ├── paso1.py           # Selección y validación de archivos
│   ├── paso2.py           # Verificación con previsualizador
│   ├── paso3.py           # Proceso de envío con progreso
│   ├── paso_ajustes.py    # Configuración de credenciales
│   └── paso_completado.py # Resumen final y estadísticas
├── logic/                  # Lógica de negocio
│   ├── email_sender.py     # Envío SMTP y encriptación PDFs
│   ├── file_handler.py     # Lectura y análisis archivos
│   ├── settings.py         # Gestión configuración cifrada
│   └── security.py         # Cifrado de credenciales
└── settings_template.ini   # Plantilla configuración
```

## 🖥️ Interfaz de Usuario

### Navegación
- **Estilo Windows clásico**: Colores `#f0f0f0`, fuentes "MS Sans Serif"
- **Validación de flujo**: No permite avanzar sin completar pasos
- **Panel lateral**: Muestra progreso visual del proceso

### Pantallas Principales

#### 1. Paso 1 - Selección de Archivos
- **Entrada**: PDF maestro + archivo empleados (CSV/Excel)
- **Auto-detección**: Mapeo automático de columnas
- **Vista previa**: Muestra datos del archivo de empleados
- **Validación**: Verifica formato y contenido

#### 2. Paso 2 - Verificación (⭐ NUEVA FUNCIONALIDAD)
- **Estadísticas**: Contador de OK/Errores/Total
- **Previsualizador PDF**: Vista previa de cada página al editar
- **Corrección manual**: Diálogo modal para editar datos
- **Estados visuales**: Verde/Rojo/Amarillo para fácil identificación

#### 3. Paso 3 - Envío
- **Progreso en tiempo real**: Barra de progreso y estado por correo
- **Estadísticas live**: Contadores de enviados/errores
- **Thread separado**: No bloquea la UI durante envío

#### 4. Configuración
- **Cifrado automático**: Credenciales se cifran al guardar
- **Validación completa**: Campos obligatorios y formatos
- **Backup automático**: Respaldo antes de cambios

## 🔧 Componentes Técnicos

### Gestión de Estado
- **Controller principal**: `GestorNominasApp` en `main_window.py`
- **Variables compartidas**: `pdf_path`, `empleados_path`, `mapa_columnas`
- **Datos de verificación**: `tareas_verificacion` para todo el flujo

### Seguridad
- **Cifrado**: Fernet (AES 128) para credenciales sensibles
- **Clave única**: Generada automáticamente por instalación
- **Archivos protegidos**: `.secret_key` oculto, settings.ini en .gitignore

### Procesamiento de Archivos
- **PDFs**: PyMuPDF (fitz) para lectura y manipulación
- **Excel/CSV**: pandas para análisis de datos
- **Encriptación PDFs**: pikepdf para proteger archivos individuales

### Email
- **SMTP**: Configuración flexible de servidores
- **Attachments**: PDFs encriptados como adjuntos
- **Threading**: Envío en background con callbacks

## 🎛️ Configuración

### settings.ini (Cifrado)
```ini
[Email]
email_origen = usuario@empresa.com
password = enc_<password_cifrada>

[SMTP]
servidor = smtp.gmail.com
puerto = 587

[PDF]
password_autor = enc_<password_cifrada>

[Carpetas]
salida = nominas_individuales
```

### Variables de Entorno Soportadas
- Ninguna actualmente - toda la configuración va por GUI

## 📊 Logging y Monitoreo

### Logs Automáticos
```python
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
```

### Puntos de Logging
- Inicio/fin de proceso de envío
- Cada correo enviado exitosamente  
- Errores de SMTP y validación
- Estadísticas finales

## 🔍 Funcionalidades Avanzadas

### Previsualizador PDF
- **Librería**: PIL (Pillow) para conversión imagen
- **Escalado**: Redimensionado automático a 400px
- **Fallback**: Funciona sin PIL con mensaje informativo
- **Performance**: Cache de imágenes en memoria

### Corrección Manual
- **Persistencia**: Correcciones almacenadas hasta envío
- **Validación**: Email y campos obligatorios
- **UI intuitiva**: Layout de dos columnas con preview

### Auto-detección Columnas
```python
nif_patterns = ['nif', 'dni', 'cedula', 'identificacion', 'id']
nombre_patterns = ['nombre', 'name', 'apellido', 'empleado']
email_patterns = ['email', 'mail', 'correo', 'electronico']
```

## 🐛 Debugging

### Errores Comunes
1. **ImportError**: Falta librería → Instalar con pip
2. **tkinter.TclError**: Conflicto geometry managers → Revisar pack/grid
3. **fitz.fitz.FileNotFoundError**: PDF no existe → Validar paths
4. **smtplib.SMTPAuthenticationError**: Credenciales incorrectas → Revisar configuración

### Testing Local
```bash
cd sistema_nominas
python main.py
```

### Variables de Debug
- Ver logs en consola para trazabilidad
- Usar `print()` temporal para debugging
- Archivos temporales en carpeta de salida

## 🚀 Deployment

### Para Desarrolladores
1. Modificar código
2. Probar localmente con `python main.py`
3. Ejecutar `python ../build.py` para generar ejecutable
4. Probar ejecutable en `../dist/`

### Para Usuarios Finales
- Descargar `EnviarNominas.exe`
- Ejecutar directamente
- Configurar en primera ejecución

## 📈 Performance

### Optimizaciones Implementadas
- **Threading**: Envío no bloquea UI
- **Lazy loading**: PDFs se cargan solo cuando necesario
- **Memory cleanup**: Liberación explícita de recursos
- **Batch processing**: Procesamiento eficiente de archivos grandes

### Limitaciones Conocidas
- **Memoria**: PDFs muy grandes (>100MB) pueden ser lentos
- **Threading**: Solo un envío a la vez
- **UI**: No responsive durante carga inicial de archivos grandes

---

**Para más información, consulte el README principal del proyecto.**