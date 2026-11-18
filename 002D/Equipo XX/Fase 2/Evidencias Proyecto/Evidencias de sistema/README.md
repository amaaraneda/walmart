# Evidencias de sistema

Góndola Visión · Corte del 17 de noviembre de 2026

## Aplicación

Probamos la web en Microsoft Edge con una cuenta de demostración, dos fotografías del piloto y el modelo principal. Las capturas públicas conservan la interfaz y los resultados. Las fotografías del piloto y las imágenes anotadas se resguardan en el archivo local del equipo.

| Entrada | Resultado observado | Evidencia |
|---|---|---|
| supermarket_021.jpg | HTTP 200. 82,8 % de ocupación frontal estimada en cuatro niveles. | [Captura web](Aplicaci%C3%B3n/Demo%20caso%20021.jpg) |
| supermarket_001.jpg | HTTP 200. Sin porcentaje por falta de niveles estables. | [Captura web](Aplicaci%C3%B3n/Demo%20caso%20001.jpg) |
| Archivo TXT | HTTP 415. Se admiten JPG, PNG y WebP. | [Registro HTTP](Aplicaci%C3%B3n/pruebas_api.json) |

[Registro de interfaz](Aplicaci%C3%B3n/Pruebas%20interfaz.json). La suite del proyecto registró 36 pruebas aprobadas. Las dos solicitudes de API registraron 15,664 s y 0,604 s en escenas distintas. La primera incluye la carga del modelo. La meta de 5 s requiere una medición controlada en el equipo de destino.

## Base de datos

El ensayo se ejecutó por separado de la aplicación en PostgreSQL 18.6 embebido mediante PGlite. El esquema creó nueve tablas. Con datos ficticios se consultaron dos niveles y se comprobó que el motor rechazara un correo duplicado, una cobertura fuera de rango y una referencia inexistente.

Para repetir la consulta, usar una base de pruebas vacía con la extensión `uuid-ossp` disponible. Desde la carpeta `Base de datos`, ejecutar:

```powershell
psql -d gondola_pruebas -v ON_ERROR_STOP=1 -f "../../Evidencias de documentación/Script.sql"
psql -d gondola_pruebas -v ON_ERROR_STOP=1 -f "Datos de prueba.sql"
psql -d gondola_pruebas -v ON_ERROR_STOP=1 -f "Consulta de verificacion.sql"
```

[Resultados y restricciones verificadas](Base%20de%20datos/Resultado%20base%20de%20datos.json).
