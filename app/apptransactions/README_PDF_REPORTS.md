# Sistema de Reportes PDF para Transacciones

## Descripción

Se ha implementado un sistema completo de generación de reportes PDF para documentos de transacciones en la aplicación `apptransactions`. El sistema permite generar documentos PDF profesionales con formato de factura/recibo para cualquier tipo de documento de transacción.

## Características

### 🎨 Diseño Profesional
- **Formato limpio y profesional** similar a una factura de venta
- **Encabezado** con logo de la empresa y título del documento
- **Cuerpo** con información detallada del documento y líneas de productos
- **Pie de página** con firmas y información del sistema
- **Responsive** y optimizado para impresión A4

### 📊 Información Incluida
- **Datos del documento**: Número, fecha, tipo, creador
- **Información del cliente/proveedor**: Datos del builder asociado
- **Información de la obra**: Work Account con builder, job, modelo de casa, dirección
- **Líneas de productos**: Producto, cantidad, unidad, precio, descuentos
- **Totales**: Subtotal, descuentos, total final
- **Observaciones**: Notas del documento si las hay
- **Firmas**: Espacios para firma del emisor y receptor

### 🏢 Logos por Tenant
El sistema detecta automáticamente el logo según el dominio:
- `phoenixelectricandair` → Logo Phoenix
- `division16llc` o `192.168.0.248:8000` → Logo Division16
- Otros dominios → Logo por defecto

## Archivos Implementados

### 1. Template HTML
**Archivo**: `apptransactions/templates/transaction_pdf.html`

Template profesional con:
- Bootstrap 5 para estilos
- CSS personalizado para PDF
- Estructura responsive
- Formato de tabla para productos
- Secciones organizadas

### 2. Vista de Generación
**Archivo**: `apptransactions/views.py` (función `download_transaction_pdf`)

Funcionalidades:
- Autenticación requerida
- Optimización de consultas con `select_related` y `prefetch_related`
- Manejo de errores robusto
- Generación de PDF con WeasyPrint
- Codificación base64 para respuesta

### 3. URL de Acceso
**Archivo**: `apptransactions/urls.py`

Endpoint agregado:
```python
path('api/documents/<int:document_id>/pdf/', download_transaction_pdf, name='download-transaction-pdf')
```

## Uso del Sistema

### Endpoint
```
GET /api/documents/{document_id}/pdf/
```

### Autenticación
Requiere token de autenticación en el header:
```
Authorization: Token {your_token}
```

### Respuesta
```json
{
    "file": "base64_encoded_pdf_content",
    "filename": "INCOME_123.pdf",
    "file_type": "application/pdf"
}
```

### Ejemplo de Uso desde Frontend

```javascript
// Función para descargar PDF de transacción
async function downloadTransactionPDF(documentId) {
    try {
        const response = await fetch(`/api/documents/${documentId}/pdf/`, {
            method: 'GET',
            headers: {
                'Authorization': `Token ${authToken}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Error al generar PDF');
        }

        const data = await response.json();
        
        // Crear blob y descargar
        const byteCharacters = atob(data.file);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], {type: 'application/pdf'});
        
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = data.filename;
        link.click();
        window.URL.revokeObjectURL(url);
        
    } catch (error) {
        console.error('Error:', error);
    }
}
```

## Tipos de Documentos Soportados

El sistema funciona con **cualquier tipo de documento** definido en `DocumentType`:
- **Ventas**: INCOME, SALES, etc.
- **Compras**: PURCHASE, EXPENSE, etc.
- **Ajustes**: ADJUSTMENT_IN, ADJUSTMENT_OUT, etc.
- **Movimientos**: PICK, TRANSFER, etc.
- **Operacionales**: Cualquier documento con Work Account

## Dependencias

### Backend
- `weasyprint`: Para generación de PDF
- `django`: Framework base
- `djangorestframework`: Para API

### Frontend (opcional)
- `base64` decoding para manejo de archivos
- `Blob API` para descarga

## Estructura de Datos

### Document
- `document_type`: Tipo de documento
- `date`: Fecha del documento
- `builder`: Cliente/proveedor
- `work_account`: Cuenta de trabajo (opcional)
- `notes`: Observaciones
- `total_amount`: Total del documento
- `total_discount`: Descuento total

### DocumentLine
- `product`: Producto
- `quantity`: Cantidad
- `unit`: Unidad de medida
- `unit_price`: Precio unitario
- `discount_percentage`: Porcentaje de descuento
- `final_price`: Precio final
- `brand`: Marca del producto
- `price_type`: Tipo de precio

## Personalización

### Modificar Estilos
Editar el archivo `transaction_pdf.html` en la sección `<style>`.

### Agregar Campos
1. Modificar el template HTML para mostrar nuevos campos
2. Actualizar la vista para incluir los datos en el contexto
3. Asegurar que las relaciones estén incluidas en las consultas

### Cambiar Logo
Modificar la lógica en `download_transaction_pdf` para detectar nuevos dominios.

## Pruebas

Para probar el sistema:

1. **Verificar datos existentes**:
   ```bash
   python manage.py shell -c "from apptransactions.models import Document; print('Documentos:', Document.objects.count())"
   ```

2. **Probar endpoint**:
   ```bash
   curl -H "Authorization: Token YOUR_TOKEN" http://localhost:8000/api/documents/1/pdf/
   ```

3. **Verificar generación**: El endpoint debería retornar un JSON con el PDF codificado en base64.

## Consideraciones de Rendimiento

- **Consultas optimizadas**: Uso de `select_related` y `prefetch_related`
- **Cache de fuentes**: `FontConfiguration()` para mejorar rendimiento
- **Manejo de errores**: Try/catch robusto para evitar fallos
- **Respuesta eficiente**: PDF generado en memoria y codificado en base64

## Mantenimiento

### Logs
El sistema registra errores en los logs de Django para debugging.

### Monitoreo
Verificar que WeasyPrint esté funcionando correctamente y que los templates se rendericen sin errores.

### Actualizaciones
Para actualizar el formato del PDF, solo modificar el template HTML. Los cambios se reflejan inmediatamente.
