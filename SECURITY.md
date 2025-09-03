# 🔒 Configuración de Seguridad

## Protección de Credenciales

Esta aplicación ahora incluye **cifrado automático** de credenciales sensibles para proteger:

- ✅ Contraseñas de email
- ✅ Contraseñas de edición de PDFs  
- ✅ Otros datos sensibles

## Primera Configuración

### 1. Configuración Automática
Al ejecutar la aplicación por primera vez:

1. Se creará un archivo `settings.ini` vacío
2. Vaya a **"Configuración"** en la aplicación
3. Complete sus credenciales
4. Las contraseñas se cifrarán automáticamente

### 2. Configuración Manual (Avanzada)

Si prefiere configurar manualmente:

```bash
# 1. Copie el archivo plantilla
cp settings_template.ini settings.ini

# 2. Edite sus credenciales
# Las contraseñas se cifrarán automáticamente al guardar desde la app
```

## Archivos Importantes

- `settings.ini` - Su configuración (CIFRADA automáticamente)
- `.secret_key` - Clave de cifrado (NO COMPARTIR)
- `settings_template.ini` - Plantilla para nuevos usuarios

## ⚠️ IMPORTANTE para Empresas

### Backup de Seguridad
```bash
# Respaldar la configuración cifrada
cp settings.ini settings.ini.empresa.backup
cp .secret_key .secret_key.empresa.backup
```

### Si Pierde la Clave
Si pierde el archivo `.secret_key`:

1. Vaya a Configuración → "Resetear Configuración"  
2. Vuelva a introducir sus credenciales
3. Se generará una nueva clave automáticamente

### Control de Acceso
- ✅ El archivo `.secret_key` se marca como oculto en Windows
- ✅ Todos los archivos sensibles están en `.gitignore`
- ✅ Backup automático antes de cada cambio

## Solución de Problemas

### Error: "Cifrado no disponible"
```bash
# Instalar la librería de cifrado
pip install cryptography
```

### Error al cargar configuración
1. Verificar que `settings.ini` existe y no está corrupto
2. Si persiste: eliminar `settings.ini` y `.secret_key` 
3. Volver a configurar desde la aplicación