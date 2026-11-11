# Tienda de Moda Circular - App Streamlit + Oracle

Aplicación web desarrollada en **Streamlit** y conectada a una base de datos **Oracle** para la gestión integral de ventas, clientes, prendas y canales en un modelo de negocio de moda circular.

---

## Requisitos del Sistema y Librerías

Para ejecutar la aplicación correctamente, se requiere Python 3.10+ y las siguientes librerías:

```bash
pip install streamlit oracledb pandas altair
```

*(Librerías principales empleadas: `streamlit` para la interfaz web, `oracledb` para la conexión a la base de datos Oracle, `pandas` para el tratamiento de datos y `altair` para la visualización gráfica).*

---

## Orden de Ejecución de los Scripts SQL

Para configurar la base de datos en Oracle, se deben ejecutar los scripts ubicados en la carpeta `Trabajo Final` en el siguiente orden secuencial estricto:

1. [**`01_DDLsql`**](./Trabajo%20Final/01_DDLsql): Crea la estructura de la base de datos. Incluye la definición de tablas, llaves primarias (`PK`), llaves foráneas (`FK`), reglas de integridad y restricciones (`NOT NULL`, `CHECK`, `UNIQUE`).
2. [**`02_DMLsql`**](./Trabajo%20Final/02_DMLsql): Carga el conjunto de datos iniciales coherentes que garantizan la integridad referencial y permiten probar todas las vistas, métricas y funciones de la app.

---

## Configuración de Credenciales (`secrets.toml`)

Por motivos de seguridad, las credenciales de acceso a la base de datos Oracle no se suben al repositorio público. 

Si ejecutas el proyecto localmente, debes crear el archivo de credenciales de la siguiente manera:

### Ubicación exacta del archivo:
`Trabajo Final/.streamlit/secrets.toml`

### Pasos para crearlo desde PyCharm:
1. Abre el proyecto en **PyCharm** y ve al panel izquierdo (explorador de archivos).
2. Haz clic derecho sobre la carpeta **`Trabajo Final`** > **New** > **Directory** y ponle de nombre **`.streamlit`** (con el punto al inicio).
3. Haz clic derecho sobre la carpeta recién creada `.streamlit` > **New** > **File** y ponle de nombre **`secrets.toml`**.
4. Abre el archivo `secrets.toml` y pega el siguiente código, reemplazando los campos con las credenciales de tu base de datos Oracle:

```toml
[oracle]
user = "tu_usuario_oracle"
password = "tu_password_oracle"
# Si es local: "localhost:1521/XEPDB1" | Si es Oracle Cloud: el nombre del servicio TNS (ej: "tienda_high")
dsn = "tu_dsn_o_servicio"
```
---

## Instrucciones para Ejecutar la App

### Ejecución Local

1. Abre la terminal en el proyecto y ejecuta el siguiente comando desde el directorio raíz:

   ```bash
   streamlit run "Trabajo Final/app_moda.py"
   ```

2. La interfaz gráfica se abrirá automáticamente en tu navegador web predeterminado en la dirección local `http://localhost:8501`.

---

## Arquitectura de la Base de Datos

El Diagrama Entidad-Relación (ER) normalizado (3FN) con la especificación de entidades, cardinalidades y llaves se encuentra disponible en:

* [**Ver Diagrama MODA.drawio.png**](./Trabajo%20Final/Diagrama%20MODA.drawio.png)

---

## Documentación Adicional

* [**Documento del Proyecto (`.docx`)**](./Trabajo%20Final/Tienda%20de%20Moda%20Circular%20.docx): Incluye la descripción del negocio y la justificación del modelo relacional.
* [**Código Principal (`app_moda.py`)**](./Trabajo%20Final/app_moda.py): Script principal de la aplicación en Streamlit.

---

## Integrantes
* Maria Catalina Ocampo 
* Maria Fernanda Lara
