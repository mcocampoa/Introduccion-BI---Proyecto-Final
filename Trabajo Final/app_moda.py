"""
MODA CIRCULAR · App Streamlit + Oracle
======================================
Panel para gestionar ventas, clientes, prendas y canales.

Ejecutar en la terminal de PyCharm:
    streamlit run app_moda.py
"""
import datetime as dt
from contextlib import contextmanager

import altair as alt
import oracledb
import pandas as pd
import streamlit as st

MAX_FILAS = 1000

# Paleta: verde bosque, salvia, lino y ocre
BOSQUE = "#1F3D36"
SALVIA = "#7FA08F"
LINO = "#F5F6F2"
OCRE = "#C9973B"
TINTA = "#23302C"


# ================================================================
# 1. CONEXIÓN A ORACLE (POOL DE CONEXIONES)
# ================================================================
@st.cache_resource
def get_pool():
    """Crea y mantiene un pool de conexiones reutilizables hacia Oracle Cloud."""
    c = st.secrets["oracle"]
    config_dir = c.get("config_dir")
    extra = {}
    if c.get("lib_dir"):
        # Windows (modo Thick con Instant Client)
        oracledb.init_oracle_client(lib_dir=c["lib_dir"], config_dir=config_dir)
    else:
        # macOS (modo Thin con wallet)
        extra = dict(
            config_dir=config_dir,
            wallet_location=c.get("wallet_location", config_dir),
            wallet_password=c.get("wallet_password"),
        )
    return oracledb.create_pool(
        user=c["user"],
        password=c["password"],
        dsn=c["dsn"],
        min=1,
        max=4,
        **extra,
    )


def conexion():
    """Solicita una conexión libre del pool."""
    con = get_pool().acquire()
    esquema = st.secrets["oracle"].get("schema")
    if esquema and esquema.isidentifier():
        con.cursor().execute(f"ALTER SESSION SET CURRENT_SCHEMA = {esquema}")
    return con


def consultar(sql, **params):
    """Ejecuta un SELECT y devuelve un DataFrame."""
    con = conexion()
    try:
        cur = con.cursor()
        cur.execute(sql, params)
        columnas = [d[0].lower() for d in cur.description]
        return pd.DataFrame(cur.fetchmany(MAX_FILAS), columns=columnas)
    finally:
        con.close()


class Tx:
    """Ejecuta INSERT/UPDATE dentro de una transacción."""

    def __init__(self, con):
        self.con = con

    def run(self, sql, **params):
        cur = self.con.cursor()
        cur.execute(sql, params)
        return cur.rowcount


@contextmanager
def transaccion():
    """COMMIT o ROLLBACK automático."""
    con = conexion()
    try:
        yield Tx(con)
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


# ================================================================
# 2. PÁGINA Y ESTILOS
# ================================================================
st.set_page_config(page_title="MODA Circular", page_icon="🌿", layout="wide")

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Manrope:wght@400;500;600;700&display=swap');

    html, body, [class*="css"], .stApp {{
        font-family: 'Manrope', sans-serif;
        color: {TINTA};
    }}
    .stApp {{ background: {LINO}; }}
    .block-container {{ padding-top: 2rem; max-width: 1280px; }}
    header[data-testid="stHeader"] {{ background: transparent; }}

    /* Encabezado */
    .hero {{
        background: {BOSQUE};
        border-radius: 20px;
        padding: 2rem 2.4rem;
        margin-bottom: 1.6rem;
        display: flex; align-items: center; justify-content: space-between;
        gap: 1.5rem;
    }}
    .hero h1 {{
        font-family: 'Fraunces', serif; font-weight: 600;
        font-size: 2.5rem; line-height: 1.1; margin: 0; color: #fff;
        letter-spacing: -0.01em;
    }}
    .hero p {{ margin: .45rem 0 0; color: #C9D8D0; font-size: 1rem; }}
    .hero .sello {{
        font-size: 2.6rem; background: rgba(255,255,255,.08);
        border-radius: 50%; width: 82px; height: 82px;
        display: flex; align-items: center; justify-content: center;
        flex-shrink: 0;
    }}

    /* Títulos de sección */
    h2, h3 {{
        font-family: 'Fraunces', serif !important; font-weight: 600 !important;
        color: {BOSQUE} !important; letter-spacing: -0.01em;
    }}

    /* Tarjetas de métricas */
    div[data-testid="stMetric"] {{
        background: #fff; border: 1px solid #E3E7E2; border-radius: 16px;
        padding: 1rem 1.2rem; box-shadow: 0 1px 2px rgba(31,61,54,.05);
    }}
    div[data-testid="stMetricLabel"] p {{ color: #5E6F68; font-size: .9rem; }}
    div[data-testid="stMetricValue"] {{
        font-family: 'Fraunces', serif; color: {BOSQUE}; font-weight: 600;
    }}

    /* Pestañas */
    div[data-baseweb="tab-list"] {{ gap: .3rem; border-bottom: 1px solid #DDE3DD; }}
    button[data-baseweb="tab"] {{
        font-weight: 600; padding: .65rem 1.1rem; border-radius: 10px 10px 0 0;
        color: #5E6F68;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{ color: {BOSQUE}; }}
    div[data-baseweb="tab-highlight"] {{ background-color: {OCRE}; height: 3px; }}

    /* Tablas y formularios */
    div[data-testid="stDataFrame"] {{
        border: 1px solid #E3E7E2; border-radius: 14px; overflow: hidden;
        background: #fff;
    }}
    div[data-testid="stExpander"] {{
        background: #fff; border: 1px solid #E3E7E2; border-radius: 14px;
    }}
    div[data-testid="stForm"] {{
        border: none; padding: 0;
    }}
    .stButton > button, div[data-testid="stFormSubmitButton"] > button {{
        background: {BOSQUE}; color: #fff; border: none; border-radius: 10px;
        padding: .55rem 1.4rem; font-weight: 600;
    }}
    .stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {{
        background: #2B5248; color: #fff;
    }}
    div[data-baseweb="input"], div[data-baseweb="select"] > div {{
        border-radius: 10px;
    }}
    hr {{ border-color: #DDE3DD; }}
    </style>

    <div class="hero">
        <div>
            <h1>MODA Circular</h1>
            <p>Ventas, clientes e inventario de prendas con segunda vida.</p>
        </div>
        <div class="sello">🌿</div>
    </div>
    """,
    unsafe_allow_html=True,
)


def fechas(df):
    """Deja las columnas de fecha en formato YYYY-MM-DD."""
    for c in df.columns:
        if "fecha" in c:
            df[c] = pd.to_datetime(df[c]).dt.date
    return df


def flash(msg):
    """Guarda un mensaje en sesión y refresca la vista."""
    st.session_state["flash"] = msg
    st.rerun()


def barras(df, categoria, valor, horizontal=False, color=BOSQUE, formato=",.0f"):
    """Gráfico de barras con la paleta de la app."""
    if horizontal:
        x = alt.X(f"{valor}:Q", title=None)
        y = alt.Y(f"{categoria}:N", sort="-x", title=None)
    else:
        x = alt.X(f"{categoria}:N", sort="-y", title=None, axis=alt.Axis(labelAngle=0))
        y = alt.Y(f"{valor}:Q", title=None)
    graf = (
        alt.Chart(df)
        .mark_bar(color=color, cornerRadiusEnd=5)
        .encode(
            x=x,
            y=y,
            tooltip=[categoria, alt.Tooltip(valor, format=formato)],
        )
        .properties(height=320)
        .configure_view(strokeWidth=0)
        .configure_axis(grid=True, gridColor="#E8ECE7", labelColor="#5E6F68")
    )
    st.altair_chart(graf, width="stretch")


MONEDA = "$%d"

if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"), icon="✅")

# Prueba inicial de conexión
try:
    consultar("SELECT COUNT(*) AS n FROM dato_item")
except Exception as e:
    st.error(f"No se pudo conectar con Oracle: {e}")
    st.info(
        "Revisa `.streamlit/secrets.toml`, la lista de IPs permitidas en OCI "
        "y que las tablas existan en la base."
    )
    st.stop()

t_res, t_kardex, t_clientes, t_items, t_canales = st.tabs(
    ["Resumen", "Kardex de ventas", "Clientes", "Prendas", "Canales de venta"]
)


# ================================================================
# 3. RESUMEN
# ================================================================
with t_res:
    SQL_KPIS = """SELECT COUNT(DISTINCT kd_id_orden) AS total_ordenes, COUNT(DISTINCT kd_id_cliente) AS clientes_unicos, NVL(SUM(kd_precio_venta), 0) AS ingresos_totales, NVL(SUM(kd_costo_envio), 0) AS total_envios, NVL(AVG(kd_precio_venta), 0) AS ticket_promedio FROM kardex_moda_circular"""
    k = consultar(SQL_KPIS).iloc[0]

    c = st.columns(5)
    c[0].metric("Órdenes", int(k.total_ordenes))
    c[1].metric("Clientes únicos", int(k.clientes_unicos))
    c[2].metric("Ingresos", f"${k.ingresos_totales:,.0f}")
    c[3].metric("Envíos", f"${k.total_envios:,.0f}")
    c[4].metric("Ticket promedio", f"${k.ticket_promedio:,.0f}")

    st.write("")
    g1, g2 = st.columns(2, gap="large")

    with g1:
        st.subheader("Ingresos por canal")
        SQL_CANAL_VENTAS = """SELECT v.v_plataforma AS canal, COUNT(k.kd_id_orden) AS ordenes, SUM(k.kd_precio_venta) AS ingresos FROM kardex_moda_circular k JOIN canal_venta v ON k.kd_id_canal = v.v_id_plataforma GROUP BY v.v_plataforma ORDER BY ingresos DESC"""
        df_canal = consultar(SQL_CANAL_VENTAS)
        if df_canal.empty:
            st.info("Aún no hay ventas registradas.")
        else:
            barras(df_canal, "canal", "ingresos", color=BOSQUE)

    with g2:
        st.subheader("Prendas más vendidas")
        SQL_TOP_ITEMS = """SELECT i.i_descripcion_pieza AS prenda, COUNT(*) AS unidades_vendidas FROM kardex_moda_circular k JOIN dato_item i ON k.kd_id_item = i.i_id_item GROUP BY i.i_descripcion_pieza ORDER BY unidades_vendidas DESC"""
        df_items = consultar(SQL_TOP_ITEMS).head(10)
        if df_items.empty:
            st.info("Aún no hay prendas vendidas.")
        else:
            barras(df_items, "prenda", "unidades_vendidas", horizontal=True, color=SALVIA)


# ================================================================
# 4. KARDEX DE VENTAS
# ================================================================
with t_kardex:
    st.subheader("Movimientos del kardex")

    SQL_MOVIMIENTOS = """SELECT k.kd_id_orden AS orden, k.kd_fecha_pedido AS fecha, c.c_nombre_cliente AS cliente, i.i_descripcion_pieza AS prenda, v.v_plataforma AS canal, k.kd_precio_venta AS precio, k.kd_costo_envio AS envio FROM kardex_moda_circular k JOIN dato_cliente c ON k.kd_id_cliente = c.c_id_cliente JOIN dato_item i ON k.kd_id_item = i.i_id_item JOIN canal_venta v ON k.kd_id_canal = v.v_id_plataforma ORDER BY k.kd_id_orden DESC"""

    df_kardex = consultar(SQL_MOVIMIENTOS)
    st.dataframe(
        fechas(df_kardex),
        hide_index=True,
        width="stretch",
        column_config={
            "orden": st.column_config.NumberColumn("Orden", format="%d"),
            "fecha": "Fecha",
            "cliente": "Cliente",
            "prenda": "Prenda",
            "canal": "Canal",
            "precio": st.column_config.NumberColumn("Precio", format=MONEDA),
            "envio": st.column_config.NumberColumn("Envío", format=MONEDA),
        },
    )

    with st.expander("Registrar una venta"):
        clientes_df = consultar(
            "SELECT c_id_cliente, c_nombre_cliente FROM dato_cliente ORDER BY c_nombre_cliente"
        )
        items_df = consultar(
            "SELECT i_id_item, i_descripcion_pieza FROM dato_item ORDER BY i_descripcion_pieza"
        )
        canales_df = consultar(
            "SELECT v_id_plataforma, v_plataforma FROM canal_venta ORDER BY v_plataforma"
        )

        with st.form("nueva_venta", clear_on_submit=True):
            col1, col2 = st.columns(2, gap="large")
            with col1:
                id_orden = st.number_input(
                    "Número de orden", min_value=5000, max_value=99999, step=1
                )
                cliente_sel = st.selectbox(
                    "Cliente",
                    clientes_df["c_id_cliente"].tolist(),
                    format_func=lambda x: clientes_df[
                        clientes_df["c_id_cliente"] == x
                    ]["c_nombre_cliente"].iloc[0],
                )
                item_sel = st.selectbox(
                    "Prenda",
                    items_df["i_id_item"].tolist(),
                    format_func=lambda x: items_df[
                        items_df["i_id_item"] == x
                    ]["i_descripcion_pieza"].iloc[0],
                )
            with col2:
                canal_sel = st.selectbox(
                    "Canal de venta",
                    canales_df["v_id_plataforma"].tolist(),
                    format_func=lambda x: canales_df[
                        canales_df["v_id_plataforma"] == x
                    ]["v_plataforma"].iloc[0],
                )
                fecha_p = st.date_input("Fecha del pedido", value=dt.date.today())
                p1, p2 = st.columns(2)
                precio = p1.number_input("Precio ($)", min_value=0.0, step=1000.0)
                envio = p2.number_input("Envío ($)", min_value=0.0, step=1000.0)

            if st.form_submit_button("Guardar venta"):
                SQL_INSERT_KARDEX = """INSERT INTO kardex_moda_circular (kd_id_orden, kd_id_cliente, kd_id_item, kd_id_canal, kd_fecha_pedido, kd_precio_venta, kd_costo_envio) VALUES (:orden, :cliente, :item, :canal, :fecha_p, :precio, :envio)"""
                with transaccion() as t:
                    t.run(
                        SQL_INSERT_KARDEX,
                        orden=int(id_orden),
                        cliente=int(cliente_sel),
                        item=int(item_sel),
                        canal=int(canal_sel),
                        fecha_p=fecha_p,
                        precio=float(precio),
                        envio=float(envio),
                    )
                flash(f"Venta #{id_orden} registrada.")


# ================================================================
# 5. CLIENTES
# ================================================================
with t_clientes:
    st.subheader("Directorio de clientes")

    q_cliente = st.text_input(
        "Buscar", placeholder="Escribe un nombre", label_visibility="collapsed"
    )
    SQL_CLIENTES = """SELECT c_id_cliente AS id, c_nombre_cliente AS nombre, c_direccion_envio AS direccion, c_ciudad AS ciudad FROM dato_cliente WHERE UPPER(c_nombre_cliente) LIKE UPPER(:q) ORDER BY c_id_cliente"""

    df_cli = consultar(SQL_CLIENTES, q=f"%{q_cliente}%")
    if df_cli.empty:
        st.info("No hay clientes que coincidan con la búsqueda.")
    else:
        st.dataframe(
            df_cli,
            hide_index=True,
            width="stretch",
            column_config={
                "id": st.column_config.NumberColumn("ID", format="%d"),
                "nombre": "Nombre",
                "direccion": "Dirección de envío",
                "ciudad": "Ciudad",
            },
        )

    with st.expander("Registrar un cliente"):
        with st.form("nuevo_cliente", clear_on_submit=True):
            f1, f2 = st.columns(2, gap="large")
            id_cli = f1.number_input("ID del cliente", min_value=1, max_value=9999, step=1)
            nom_cli = f2.text_input("Nombre completo")
            dir_cli = f1.text_input("Dirección de envío")
            ciu_cli = f2.text_input("Ciudad", value="Medellín")

            if st.form_submit_button("Guardar cliente"):
                if not nom_cli.strip():
                    st.warning("Escribe el nombre del cliente para guardarlo.")
                else:
                    SQL_INSERT_CLI = """INSERT INTO dato_cliente (c_id_cliente, c_nombre_cliente, c_direccion_envio, c_ciudad) VALUES (:id_cli, :nombre, :direccion, :ciudad)"""
                    with transaccion() as t:
                        t.run(
                            SQL_INSERT_CLI,
                            id_cli=int(id_cli),
                            nombre=nom_cli.strip(),
                            direccion=dir_cli.strip(),
                            ciudad=ciu_cli.strip(),
                        )
                    flash(f"Cliente {nom_cli} registrado.")


# ================================================================
# 6. PRENDAS
# ================================================================
with t_items:
    st.subheader("Inventario de prendas")

    SQL_ITEMS = """SELECT i_id_item AS id, i_descripcion_pieza AS descripcion, i_estado_conservacion AS estado_conservacion, i_material_principal AS material FROM dato_item ORDER BY i_id_item"""

    df_it = consultar(SQL_ITEMS)
    st.dataframe(
        df_it,
        hide_index=True,
        width="stretch",
        column_config={
            "id": st.column_config.NumberColumn("ID", format="%d"),
            "descripcion": "Descripción",
            "estado_conservacion": "Estado de conservación",
            "material": "Material",
        },
    )

    with st.expander("Registrar una prenda"):
        with st.form("nuevo_item", clear_on_submit=True):
            f1, f2 = st.columns(2, gap="large")
            id_item = f1.number_input("ID de la prenda", min_value=101, max_value=9999, step=1)
            desc_item = f2.text_input("Descripción")
            est_cons = f1.selectbox(
                "Estado de conservación",
                ["Casi Nuevo", "Buen estado", "Con desgaste"],
            )
            mat_item = f2.selectbox(
                "Material principal",
                ["Algodón", "Seda", "Cuero", "Lino", "Mezclilla", "Poliéster"],
            )

            if st.form_submit_button("Guardar prenda"):
                if not desc_item.strip():
                    st.warning("Escribe la descripción de la prenda para guardarla.")
                else:
                    SQL_INSERT_ITEM = """INSERT INTO dato_item (i_id_item, i_descripcion_pieza, i_estado_conservacion, i_material_principal) VALUES (:id_item, :desc_item, :est_cons, :mat_item)"""
                    with transaccion() as t:
                        t.run(
                            SQL_INSERT_ITEM,
                            id_item=int(id_item),
                            desc_item=desc_item.strip(),
                            est_cons=est_cons,
                            mat_item=mat_item,
                        )
                    flash(f"Prenda #{id_item} registrada.")


# ================================================================
# 7. CANALES DE VENTA
# ================================================================
with t_canales:
    st.subheader("Canales de venta")

    SQL_CANALES = """SELECT v_id_plataforma AS id, v_plataforma AS plataforma, v_tipo_atencion AS tipo_atencion FROM canal_venta ORDER BY v_id_plataforma"""

    df_cv = consultar(SQL_CANALES)
    st.dataframe(
        df_cv,
        hide_index=True,
        width="stretch",
        column_config={
            "id": st.column_config.NumberColumn("ID", format="%d"),
            "plataforma": "Plataforma",
            "tipo_atencion": "Tipo de atención",
        },
    )