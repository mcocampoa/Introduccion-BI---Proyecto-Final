# Tienda de Moda Circular - App Streamlit + Oracle

Aplicación web desarrollada en Streamlit y conectada a una base de datos Oracle para la gestión integral de ventas, clientes, prendas y canales en un modelo de negocio de moda circular.

---

## Requisitos del Sistema y Librerías

Para ejecutar la aplicación correctamente, se requiere Python 3.10+ y las siguientes librerías:
bash
pip install streamlit oracledb pandas altair
(Librerías principales empleadas: `streamlit` para la interfaz web, `oracledb` para la conexión a la base de datos Oracle, `pandas` para el tratamiento de datos y `altair` para la visualización gráfica).

---

## Orden de Ejecución de los Scripts SQL

Para configurar la base de datos en Oracle, se deben ejecutar los scripts ubicados en la carpeta `Trabajo Final` en el siguiente orden secuencial estricto:

1. **`01_DDLsql`**[cite: 1]: Crea la estructura de la base de datos. Incluye la definición de tablas, llaves primarias (`PK`), llaves foráneas (`FK`), reglas de integridad y restricciones (`NOT NULL`, `CHECK`, `UNIQUE`).
2. **`02_DMLsql`**[cite: 1]: Carga el conjunto de datos iniciales coherentes que garantizan la integridad referencial y permiten probar todas las vistas, métricas y funciones de la app.

---

## Configuración de Credenciales (`secrets.toml`)

Por seguridad, las credenciales de la base de datos Oracle están desvinculadas del código fuente y se gestionan mediante el sistema de secretos de Streamlit.

Para ejecutar el proyecto en local:
1. Crear la carpeta `.streamlit` dentro de `Trabajo Final/`[cite: 1].
2. Crear el archivo `secrets.toml` en `Trabajo Final/.streamlit/secrets.toml` con la siguiente estructura:

toml
[oracle]
user = "tu_usuario_oracle"
password = "tu_password_oracle"
dsn = "tu_cadena_conexion_o_dsn"

bash
streamlit run "Trabajo Final/app_moda.py"
La interfaz gráfica se abrirá automáticamente en tu navegador web en la dirección `http://localhost:8501`[cite: 1].

---

## Arquitectura de la Base de Datos

El Diagrama Entidad-Relación (ER) normalizado (3FN) con la especificación de entidades, cardinalidades y llaves se encuentra en la raíz del proyecto en el archivo[cite: 1, 2]:
* `Diagrama sin título.drawio.png`[cite: 1]

---

## Documentación Adicional

* `Tienda de Moda Circular .docx`: Incluye la descripción del negocio y la justificación del modelo relacional[cite: 1].

---

## Integrantes
* Catalina Ocampo A.
