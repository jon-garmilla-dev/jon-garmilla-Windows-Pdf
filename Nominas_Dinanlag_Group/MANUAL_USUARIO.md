# 📖 Manual de Usuario - Asistente de Envío de Nóminas

**Guía paso a paso para secretarias y personal administrativo**

---

## 🎯 ¿Qué hace esta aplicación?

Esta aplicación le ayuda a:
- ✅ Enviar automáticamente las nóminas por correo electrónico
- 📧 Cada empleado recibe su nómina individual protegida con su NIF
- 🔒 Todo se hace de forma segura y automática
- 📊 Ve el progreso en tiempo real

---

## 🚀 Primera Vez - Configuración Inicial

### 1. Abrir la Aplicación
- Haga doble clic en `EnviarNominas.exe`
- Se abrirá una ventana con el asistente

### 2. Configurar su Email (Solo una vez)
1. Haga clic en **"Configuración"** en el panel izquierdo
2. Complete estos campos:
   - **Email de Origen**: Su email de la empresa (ej: `secretaria@empresa.com`)
   - **Contraseña**: Su contraseña de email *(se guarda cifrada)*
   - **Contraseña de PDFs**: Una contraseña para proteger la edición de PDFs
3. Haga clic en **"Guardar"**

> 💡 **Para Gmail**: Use una "contraseña de aplicación", no su contraseña normal

---

## 📋 Uso Diario - Enviar Nóminas

### PASO 1: Seleccionar Archivos 📁

1. **PDF de Nóminas**:
   - Haga clic en **"Examinar..."** junto a "PDF de Nóminas"
   - Seleccione el archivo PDF que contiene todas las nóminas del mes
   - ✅ Verá: "Archivo válido: X páginas encontradas"

2. **Archivo de Empleados**:
   - Haga clic en **"Examinar..."** junto a "Datos de Empleados"
   - Seleccione su archivo Excel o CSV con la información de empleados
   - ✅ Verá: "Archivo válido: X empleados encontrados"

3. **Asignar Columnas** (Se hace automáticamente):
   - La aplicación detecta automáticamente qué columna contiene:
     - **NIF**: Documento de identidad
     - **NOMBRE**: Nombre completo del empleado  
     - **EMAIL**: Correo electrónico
   - Si algo está mal, puede cambiar manualmente cada selección

4. Cuando todo esté correcto, el botón **"Siguiente >"** se habilitará

---

### PASO 2: Verificar Datos 🔍

Esta pantalla le muestra qué datos se encontraron automáticamente:

#### Panel Superior - Resumen
- **Total**: Cuántas nóminas se procesaron
- **Listos para envío**: Cuántos tienen todos los datos completos (✅ Verde)
- **Con problemas**: Cuántos necesitan corrección (❌ Rojo o ⚠️ Amarillo)

#### Tabla de Datos
Cada fila muestra:
- **Página**: Número de página en el PDF
- **NIF**: Documento encontrado en esa página
- **Nombre**: Nombre del empleado
- **Email**: Correo donde se enviará
- **Estado**: Si está listo o tiene problemas

#### ¿Cómo Corregir Errores?

**Para ver una nómina específica:**
- Haga clic en **"Ver PDF Completo"** para abrir todo el archivo

**Para corregir datos incorrectos:**
1. **Doble clic** en la fila que tiene error
2. Se abrirá una ventana con:
   - **Lado izquierdo**: Vista previa de esa página del PDF
   - **Lado derecho**: Campos para corregir los datos
3. Complete o corrija la información
4. Haga clic en **"Guardar"**

**Otros botones útiles:**
- **"Corregir Seleccionado"**: Corregir la fila seleccionada
- **"Volver a Verificar"**: Analizar los archivos otra vez
- **"¿Necesita Ayuda?"**: Abrir ayuda detallada

---

### PASO 3: Enviar Correos 📧

1. **Revisar** que la lista muestre solo empleados que están listos (✅)
2. Haga clic en **"Enviar a Todos"**
3. **Confirme** cuando le pregunte si está seguro

#### Durante el Envío
- Verá una **barra de progreso** que se va llenando
- Cada fila cambiará de color:
  - 🟢 **Verde**: Correo enviado exitosamente
  - 🔴 **Rojo**: Hubo un error al enviar
  - 🟡 **Amarillo**: Se está procesando

#### ¡No cierre la aplicación hasta que termine!

---

### PASO 4: Completado ✅

Al finalizar verá:
- **Estadísticas finales**: Cuántos se enviaron correctamente
- **Tiempo total**: Cuánto demoró el proceso
- **Ubicación de archivos**: Dónde se guardaron los PDFs individuales

**Opciones:**
- **"Abrir Carpeta"**: Ver los archivos PDF creados
- **"Nuevo Proceso"**: Empezar con nuevas nóminas

---

## ❓ Preguntas Frecuentes

### "No puedo enviar correos"
**Posibles causas:**
- ✅ Verifique su conexión a internet
- ✅ Confirme que su email y contraseña son correctos
- ✅ Para Gmail, asegúrese de usar "contraseña de aplicación"
- ✅ Consulte con IT si persiste el problema

### "No encuentra datos en el PDF"
**Posibles causas:**
- ✅ Verifique que el PDF tenga NIFs válidos (8 números + 1 letra)
- ✅ Use "Ver PDF Completo" para revisar el formato
- ✅ Consulte con la gestoría si el PDF está bien formado

### "Error al leer archivo de empleados"
**Posibles causas:**
- ✅ Verifique que el archivo no esté abierto en Excel
- ✅ Confirme que tiene las columnas NIF, Nombre y Email
- ✅ Use "Volver a Verificar" después de corregir el archivo

### "Las columnas no se detectan bien"
**Solución:**
- ✅ En el Paso 1, cambie manualmente la asignación de columnas
- ✅ Verifique que los nombres de columnas sean claros (ej: "NIF", "Nombre", "Email")

---

## 🔒 Información de Seguridad

- ✅ **Sus credenciales se cifran automáticamente** - nadie más puede verlas
- ✅ **Cada empleado solo puede abrir su nómina** con su NIF
- ✅ **Los PDFs están protegidos** contra modificación no autorizada
- ✅ **No se guardan datos sensibles** en archivos temporales

---

## 📞 ¿Necesita Más Ayuda?

1. **En cada pantalla**: Use el botón "¿Necesita Ayuda?"
2. **Problemas técnicos**: Contacte con el departamento de IT
3. **Problemas con archivos**: Verifique con la gestoría o contabilidad

---

## ✅ Lista de Verificación Rápida

Antes de cada envío, confirme:

- [ ] ✅ El PDF tiene todas las nóminas del mes
- [ ] ✅ El archivo de empleados está actualizado
- [ ] ✅ Su configuración de email funciona
- [ ] ✅ Tiene conexión a internet estable
- [ ] ✅ En el Paso 2, la mayoría aparecen en verde (✅ OK)
- [ ] ✅ Ha verificado manualmente algunos datos dudosos

**¡Ya está listo para enviar nóminas de forma automática y segura!**