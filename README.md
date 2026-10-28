# Motion Studio

Primera base de Motion Studio: aplicación de escritorio Windows con interfaz oscura y acento verde.

## Funciones incluidas en esta base
- Importación de imágenes PNG/JPG/WebP como capas.
- Vista previa con movimiento Float (flotar suavemente).
- Controles de velocidad, intensidad y duración.
- Exportación MP4 1080 × 1920 a 30 FPS.
- Compilación del ejecutable en GitHub Actions.

## Compilar en GitHub Actions
Sube estos archivos a un repositorio GitHub y ejecuta el workflow `Build Motion Studio for Windows` desde Actions. Descarga el artifact `MotionStudio-Windows`.

## Limitaciones de esta primera base
- La importación de una imagen completa no separa automáticamente los elementos del flyer. Para mover cada elemento por separado, importa los elementos individuales en PNG con transparencia.
- No incluye todavía IA para segmentar personas/textos, cámara 3D, keyframes avanzados ni exportación 4K.
