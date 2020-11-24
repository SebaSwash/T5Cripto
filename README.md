# T5Cripto
## Tarea 5: Autenticación alternativa de emails
### Criptografía y Seguridad en Redes (02 - 2020)
### Sebastián Ignacio Toro Severino

### Consideraciones

---

1. Asegurarse de tener instalada la librería de colores **colorama**, que permite mostrar los mensajes con otros colores en la terminal. ( ``pip install colorama / pip3 install colorama `` ).
2. Dentro de la carpeta exports se almacenan los resultados de las ejecuciones, tanto obtener la lista de MID (message id) con sus fechas de emisión, como también de los resultados al hacer match con la expresión regular configurada.
3. El programa permite modificar la configuración para seleccionar una combinación (correo emisor, regex, fecha) distinta, además de poder cambiar de buzón (mailbox).
4. El archivo para importar la lista de expresiones regulares asociadas a cada correo con sus fechas de emisión debe ser de extensión **.csv**.