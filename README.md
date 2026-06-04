# Facu Assistant

## Estado del proyecto

> Estado: Archivado
> Última actualización: 06/2026

Bot de Telegram desarrollado para registrar capacitaciones comerciales de forma estandarizada, almacenar los registros localmente en SQLite y enviarlos automáticamente a Google Forms.

El proyecto fue utilizado en un entorno real de trabajo para simplificar la carga de información, reducir errores manuales y centralizar registros de capacitaciones.

El proyecto se conserva como referencia técnica y ejemplo de automatización desarrollada para un caso de uso real.

## Tecnologías utilizadas

- Python 3.11
- Telegram Bot API
- SQLite
- Docker
- Docker Compose
- Ubuntu Server
- Google Forms
- Requests
- Python Dotenv

## Contexto

Durante las actividades de capacitación comercial era necesario registrar información de cada capacitación realizada y posteriormente cargarla en formularios de Google.

El objetivo del proyecto fue automatizar este proceso mediante un bot de Telegram que permitiera:

- Registrar capacitaciones desde el teléfono móvil.
- Validar datos antes de almacenarlos.
- Mantener una copia local de los registros.
- Enviar automáticamente la información a Google Forms.
- Reducir errores de carga manual.

## Resultado

El bot permitió:

- Estandarizar el registro de capacitaciones.
- Reducir errores de carga manual.
- Centralizar la información en Google Forms.
- Mantener respaldo local mediante SQLite.
- Simplificar la operatoria diaria desde dispositivos móviles.

## Arquitectura

Telegram
│
▼
Facu Assistant (Python)
│
├── SQLite (persistencia local)
│
└── Google Forms (registro centralizado)

### Flujo de trabajo

1. El usuario envía una capacitación mediante Telegram.
2. El bot valida el formato recibido.
3. El registro se almacena en SQLite.
4. Si el usuario no está en modo test:
   - genera el payload
   - envía los datos a Google Forms
5. Si ocurre un error, el registro permanece almacenado localmente.

## Entorno de ejecución

- Ubuntu Server
- Docker Compose
- SQLite persistida mediante volumen Docker
- Bot de Telegram ejecutado mediante polling
- Configuración mediante variables de entorno (.env)

## Estructura

```text
.
+-- facu_assistant.py      # Codigo principal del bot
+-- requirements.txt       # Dependencias Python
+-- Dockerfile             # Imagen Docker del bot
+-- docker-compose.yml     # Ejecucion con volumen persistente para SQLite
+-- .env                   # Variables reales, no versionar
+-- .env.example           # Plantilla segura de configuracion
`-- data/                  # Base SQLite generada en ejecucion, no versionar
```

## Desafíos técnicos resueltos

Durante el desarrollo se resolvieron distintos problemas técnicos:

- Validación estructurada de mensajes enviados por usuarios.
- Persistencia local mediante SQLite.
- Integración con Google Forms mediante solicitudes HTTP POST.
- Manejo de errores de comunicación externos.
- Separación de configuración sensible mediante variables de entorno.
- Despliegue en contenedores Docker.
- Persistencia de datos mediante volúmenes Docker.
- Operación continua sobre Ubuntu Server.

## Lecciones aprendidas

Este proyecto permitió adquirir experiencia práctica en:

- Desarrollo de bots para Telegram.
- Automatización de procesos administrativos.
- Diseño de flujos de validación de datos.
- Persistencia de información con SQLite.
- Contenerización con Docker.
- Administración básica de servidores Linux.
- Uso de variables de entorno para manejo de secretos.
- Documentación técnica y mantenimiento de proyectos.

## Ciclo de vida del proyecto

Inicio: 05/2025

Archivado: 06/2026

Motivo de archivado:

Finalización del proceso comercial para el cual fue desarrollado. El proyecto se conserva como referencia técnica y ejemplo de automatización aplicada a un caso de uso real.

---

## Configuración

El bot lee variables desde `.env` usando `python-dotenv`.

Variables requeridas:

| Variable | Descripcion |
| --- | --- |
| `TELEGRAM_TOKEN` | Token del bot de Telegram generado con BotFather. |
| `FORM_URL` | URL de envio del formulario de Google Forms. |
| `DB_PATH` | Ruta de la base SQLite. En Docker se usa normalmente `/data/app.db`. |

Ejemplo:

```env
TELEGRAM_TOKEN=123456789:telegram-token
FORM_URL=https://docs.google.com/forms/d/e/FORM_ID/formResponse
DB_PATH=/data/app.db
```

No guardar tokens reales ni URLs privadas en documentacion o commits.

## Formato de mensaje

El bot espera 7 u 8 lineas. La octava linea, comentarios, es opcional.

```text
DD-MM-YY
Capacitador
Cadena
Zona
Direccion
Cantidad
Vendedores
Comentarios
```

Ejemplo:

```text
09-01-26
Facundo Perez
Cadena Ejemplo
Zona Norte
Av. Siempre Viva 123
5
Juan Gomez, Maria Lopez
Sin observaciones
```

Reglas de validacion:

- La fecha debe tener formato `DD-MM-YY`.
- `capacitador`, `cadena`, `zona`, `direccion` y `cantidad` son obligatorios.
- `cantidad` debe ser un entero de 0 o mas.
- `vendedores` puede ser `-` si no aplica.
- Si hay varios vendedores, se aceptan separados por coma o punto y coma.

## Comandos de Telegram

| Comando | Uso |
| --- | --- |
| `/test` | Muestra si el modo test esta activado para el usuario actual. |
| `/test on` | Activa modo test. Los registros se guardan en SQLite pero no se envian a Google Forms. |
| `/test off` | Desactiva modo test. Los registros validos se envian a Google Forms. |
| `/comentario <texto>` | Guarda un comentario libre asociado al usuario. |
| `/comentarios` | Muestra los ultimos 10 comentarios del usuario. |
| `/comentarios N` | Muestra hasta `N` comentarios, con limite maximo de 50. |

## Base de datos

La base SQLite se inicializa automaticamente al arrancar el bot.

### trainings

Almacena capacitaciones registradas, estado de envío a Google Forms y posibles errores.

### comments

Almacena comentarios libres asociados a usuarios de Telegram.

## Envio a Google Forms

La funcion `enviar_a_forms` arma un `payload` con los campos `entry.*` del formulario y hace un `POST` a `FORM_URL`.
Si el envio falla, el registro igual se guarda en SQLite con `sent_to_forms = 0` y el error queda en `forms_error`.

## Ejecución local

Crear un entorno virtual, instalar dependencias y ejecutar el bot:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python facu_assistant.py
```

El archivo `.env` debe existir antes de iniciar el bot.

## Ejecución con Docker Compose

Construir y levantar:

```powershell
docker compose up -d --build
```

Ver logs:

```powershell
docker compose logs -f facu-assistant
```

Detener:

```powershell
docker compose down
```

La base SQLite queda persistida en `./data` por el volumen configurado:

```yaml
volumes:
  - ./data:/data
```

## Consideraciones de archivo

- `.env` contiene secretos y debe mantenerse fuera de Git.
- `data/` contiene la base SQLite y tambien queda fuera de Git.
- Si se restaura el proyecto, revisar que `FORM_URL` siga correspondiendo al mismo Google Form. Si el formulario cambia, los IDs `entry.*` pueden dejar de coincidir.
- El modo test es por usuario y vive en `context.user_data`, por lo que no necesariamente sobrevive reinicios del proceso.
- El bot usa polling de Telegram, no webhook.
- El codigo no incluye tests automatizados.
- Si los mensajes del bot muestran caracteres extranos, revisar que el archivo este guardado como UTF-8 y que la consola/editor no lo este leyendo con otra codificación.

## Licencia  
  
Este proyecto se distribuye bajo la licencia MIT.  
  
Puede utilizarse, modificarse y redistribuirse respetando los términos indicados en el archivo `LICENSE`.  
