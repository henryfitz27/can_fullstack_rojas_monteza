# Funcionalidad de Subida de Archivos

Esta funcionalidad permite a los usuarios subir archivos TXT o CSV que contengan links para ser procesados por el sistema.

## Características

- **Drag & Drop**: Arrastra y suelta archivos directamente en la zona de subida
- **Validación de archivos**: Solo acepta archivos TXT y CSV
- **Límite de tamaño**: Máximo 1MB por archivo
- **Progreso visual**: Barra de progreso durante la subida
- **Notificaciones**: Mensajes de éxito y error con Toast notifications
- **Validación en tiempo real**: Verificación inmediata del tipo y tamaño del archivo

## Formatos Soportados

### Archivos TXT
Los archivos TXT deben contener un link por línea:
```
https://ejemplo1.com
https://ejemplo2.com
https://ejemplo3.com
```

### Archivos CSV
Los archivos CSV pueden contener links en cualquier columna, con o sin encabezados:
```csv
url,descripcion,categoria
https://ejemplo1.com,Primer enlace,Categoría A
https://ejemplo2.com,Segundo enlace,Categoría B
```

## Uso

1. Navega a `/admin/files/create`
2. Arrastra un archivo a la zona de subida o haz clic para seleccionar
3. El archivo se validará automáticamente
4. Haz clic en "Subir archivo" para enviarlo al servidor
5. Se mostrará el progreso de la subida
6. Una vez completado, se redirigirá automáticamente a la lista de archivos

## Validaciones

- **Tipo de archivo**: Solo TXT y CSV
- **Tamaño máximo**: 1MB (1,048,576 bytes)
- **Cantidad**: Solo un archivo a la vez

## Endpoint de API

La subida se realiza mediante una server action que envía el archivo al endpoint:
- **URL**: `/upload`
- **Método**: POST
- **Body**: FormData con el campo `file`
- **Headers**: Authorization Bearer token

## Componentes

- `FileDropzone`: Componente principal de drag & drop
- `ProgressBar`: Barra de progreso visual
- `uploadFile`: Server action para manejar la subida

## Archivos de Ejemplo

Se incluyen archivos de ejemplo:
- `sample-links.txt`: Ejemplo de formato TXT
- `sample-links.csv`: Ejemplo de formato CSV

## Tecnologías Utilizadas

- **react-dropzone**: Para la funcionalidad de drag & drop
- **Next.js Server Actions**: Para el manejo del lado servidor
- **sonner**: Para las notificaciones toast
- **Tailwind CSS**: Para el diseño y estilos
- **Radix UI**: Para los componentes base
