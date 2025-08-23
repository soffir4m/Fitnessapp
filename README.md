Fitnessapp - Proyecto Final Curso de Programación Web
Equipo

Junior Ramírez
Melany Ramírez
Jason Barrantes
Jasser Palacios

Descripción
Fitnessapp es una aplicación web desarrollada como proyecto final del curso de Programación Web en el Bachillerato en Ingeniería en Ciencia de Datos de LEAD University, bajo la dirección del profesor Alejandro Zamora. Este proyecto integra todos los conocimientos adquiridos en el curso, incluyendo frontend, backend, orquestación de pipelines, seguridad de datos, base de datos y DevOps. La aplicación ofrece un CRUD completo, consume una API externa, expone una API interna y utiliza un pipeline de datos para limpieza, registro de logs y generación de backups automáticos, todo enfocado en el ámbito del fitness.
Tecnologías y Herramientas

Frontend:
HTML5 semántico
CSS3 (Flexbox o Grid)
JavaScript ES6+ (Fetch API, módulos)


Backend:
Python 3.9+ con FastAPI
Pydantic para validación de modelos
mysql-connector-python o SQLAlchemy ORM


Pipelines (elige una):
Prefect 2.x (Flows, Tasks, Orion, Agent)
Apache Airflow (DAGs, Operators, Scheduler)


Seguridad de Datos:
HTTPS (certificados TLS)
Sanitización/validación de inputs (inyección SQL, XSS)
Manejo de secretos (Vault, variables de entorno, Prefect Secrets)


Base de Datos:
MySQL o PostgreSQL
Diseño de esquemas normalizados
Scripts SQL para migraciones y carga inicial


DevOps/Despliegue:
Docker / Docker Compose
Pipelines CI/CD (GitHub Actions, GitLab CI)
Despliegue en la nube (Heroku, Render, AWS EC2, GCP Cloud Run)



Requerimientos Funcionales

CRUD Principal:
Usuarios podrán crear, leer, actualizar y eliminar recursos (ejemplo: ejercicios, rutinas, progresos).


API Externa:
Consumir datos de al menos una API pública (e.g., OpenWeatherMap, TheMealDB) y mostrarlos en el frontend.


API Interna:
Exponer rutas REST (/api/...) para realizar operaciones contra la base de datos local.


Pipeline de Datos:
ETL automático que extrae datos crudos (RAW) de la base de datos o API externa, transforma/limpia (elimina nulos, formatea, valida rangos), carga en tablas 'cleaned', genera logs (TXT o JSON) con métricas, y crea backups periódicos en CSV (carpeta backups/).
Programado con Prefect u Airflow.


Seguridad:
Toda conexión HTTP debe usar HTTPS.
Validar y sanitizar entradas de usuario.
Proteger credenciales de la base de datos y APIs externas.


Despliegue & DevOps:
Contenerización con Docker.
CI/CD que ejecute pruebas básicas y despliegue a staging o producción.
Documentar pasos de despliegue en README.md.



Instalación y Ejecución Local

Clona el repositorio:git clone https://github.com/soffir4m/Fitnessapp.git
cd Fitnessapp


Configura el entorno:
Instala Docker y Docker Compose.
Crea un archivo .env con las variables de entorno (credenciales de DB, claves de API).


Levanta los servicios:docker-compose up --build


Accede a la UI en http://localhost:8000 y a la documentación de la API en /docs (Swagger UI).

Cómo Disparar el Pipeline Manualmente

Ejecuta el comando correspondiente al orquestador elegido (Prefect o Airflow) desde la carpeta pipeline/, según la configuración del proyecto.

Estructura del Proyecto

frontend/: HTML, CSS, JS.
backend/: Python, FastAPI, scripts de pipeline.
pipeline/: Flows o DAGs, backups, logs.
sql/: Scripts SQL para tablas y datos de prueba.
.github/workflows/: Workflow de CI/CD.

Licencia
Este proyecto se encuentra bajo una licencia educativa, sin fines comerciales.
