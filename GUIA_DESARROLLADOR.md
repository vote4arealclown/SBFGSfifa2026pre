# Guía del Desarrollador — Smart Bet Field Guide System 2026

> **Para contribuidores, mantenedores y cualquiera que quiera extender la plataforma.**

---

## Tabla de Contenidos

1. [Visión General de la Arquitectura](#visión-general-de-la-arquitectura)
2. [Primeros Pasos (Desarrollo)](#primeros-pasos-desarrollo)
3. [Capa de Base de Datos](#capa-de-base-de-datos)
4. [Pipeline de Ingesta de Datos](#pipeline-de-ingesta-de-datos)
5. [Agregar Nuevas Fuentes de Datos](#agregar-nuevas-fuentes-de-datos)
6. [Módulo de Reportes](#módulo-de-reportes)
7. [Utilidades de Apuestas](#utilidades-de-apuestas)
8. [Desarrollo de la TUI](#desarrollo-de-la-tui)
9. [Desarrollo de la CLI](#desarrollo-de-la-cli)
10. [Pruebas y Validación](#pruebas-y-validación)
11. [Lista de Verificación de Lanzamiento](#lista-de-verificación-de-lanzamiento)

---

## Visión General de la Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                        PRESENTACIÓN                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  TUI         │  │  CLI         │  │  Jupyter     │      │
│  │  (Textual)   │  │  (argparse)  │  │  (pandas)    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼─────────────────┼─────────────────┼──────────────┘
          │                 │                 │
          └─────────────────┴─────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────┐
│                      LÓGICA DE NEGOCIO                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  reports.py  │  │betting_utils │  │  seed_field  │      │
│  │  (consultas) │  │  (prob, EV)  │  │  _guide.py   │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼─────────────────┼─────────────────┼──────────────┘
          │                 │                 │
          └─────────────────┴─────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────┐
│                        CAPA DE DATOS                         │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              SQLite (fifa2026_repo.db)               │    │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐  │    │
│  │  │ jugad.  │ │ partid. │ │ eventos │ │  sedes   │  │    │
│  │  └─────────┘ └─────────┘ └─────────┘ └──────────┘  │    │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐  │    │
│  │  │  nivel  │ │penales  │ │escenar. │ │glosario  │  │    │
│  │  └─────────┘ └─────────┘ └─────────┘ └──────────┘  │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                      FUENTES DE DATOS                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Histórico    │  │ Field Guide  │  │  Futuro:     │      │
│  │ Open Data    │  │  Referencia  │  │  Odds API,   │      │
│  │  (2022 CM)   │  │   (manual)   │  │  Clima,      │      │
│  │              │  │              │  │  Transferm.  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Principios de Diseño

1. **Local-first:** Todo corre en tu máquina. No se necesitan claves de API para el dataset central.
2. **Modular:** Cada módulo tiene una sola responsabilidad. Puedes cambiar el módulo de ingesta por otra fuente sin tocar la UI.
3. **SQLite:** Base de datos sin configuración. No Docker, no Postgres, no nube.
4. **Extensible:** Nuevos reportes, tablas y fuentes de datos se integran limpiamente.

---

## Primeros Pasos (Desarrollo)

### Prerrequisitos

- Python 3.10 o superior
- `make` (opcional, para la conveniencia del Makefile)
- `uv` o `pip` para gestión de paquetes

### Configuración de Desarrollo

```bash
# Clonar el repositorio
git clone https://github.com/yourusername/sbfg2026.git
cd sbfg2026

# Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar en modo editable con todos los extras
pip install -e ".[analytics,notebook,dev]"

# Cargar datos de referencia
python src/seed_field_guide.py

# Ejecutar pruebas
make test
```

### Convenciones de Estructura

```
src/
  database.py            # Esquema + conexión (sin lógica de negocio)
  ingest_<fuente>.py     # Un archivo por fuente de datos externa
  seed_<dominio>.py      # Un archivo por dominio de datos de referencia
  reports.py             # Todas las consultas SQL retornan DataFrames de pandas
  betting_utils.py       # Funciones puras, sin efectos secundarios
  cli.py                 # Comandos argparse llaman a reports + utils
  tui_app.py             # Pantallas Textual componen reports + utils
```

---

## Capa de Base de Datos

### Agregar una Nueva Tabla

1. Agrega la sentencia `CREATE TABLE` a `database.py` en `SCHEMA_SQL`.
2. Ejecuta `python src/database.py` para aplicar el esquema.
3. Agrega datos semilla en un script `seed_*.py`.
4. Agrega una función de reporte en `reports.py`.
5. Conéctala a la CLI (`cli.py`) y TUI (`tui_app.py`).

### Ejemplo: Agregar una tabla `historial_clima`

```python
# En database.py, agregar a SCHEMA_SQL:
"""
CREATE TABLE IF NOT EXISTS historial_clima (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sede_id INTEGER,
    fecha_partido TEXT,
    temperatura_c REAL,
    humedad_pct REAL,
    precipitacion_mm REAL,
    velocidad_viento_kmh REAL,
    FOREIGN KEY (sede_id) REFERENCES venues_2026(venue_id)
);
CREATE INDEX IF NOT EXISTS idx_clima_sede ON historial_clima(sede_id);
CREATE INDEX IF NOT EXISTS idx_clima_fecha ON historial_clima(fecha_partido);
"""

# Script semilla: src/seed_clima.py
from database import execute_many

def seed_clima(db_path=None):
    registros = [
        # (sede_id, fecha_partido, temperatura_c, humedad_pct, ...)
    ]
    query = "INSERT INTO historial_clima (...) VALUES (?, ?, ?, ?, ?, ?)"
    execute_many(query, registros, db_path)

# Función de reporte: en reports.py
def report_clima_por_sede(db_path=None):
    query = """
        SELECT * FROM historial_clima 
        JOIN venues_2026 ON historial_clima.sede_id = venues_2026.venue_id
    """
    return _df_from_query(query, db_path=db_path)
```

### Gestión de Conexiones

Usa siempre el gestor de contexto:

```python
from database import get_connection

with get_connection() as conn:
    filas = conn.execute("SELECT * FROM players WHERE goals > 5").fetchall()
    for fila in filas:
        print(dict(fila))
```

El gestor de contexto maneja automáticamente:
- Fábrica `sqlite3.Row` (acceso tipo diccionario)
- Limpieza de conexiones

---

## Pipeline de Ingesta de Datos

### Agregar una Nueva Fuente de Datos

Crea `src/ingest_<fuente>.py` siguiendo este patrón:

```python
"""Ingesta datos desde <Nombre de Fuente>."""

from database import execute_many, get_connection

SOURCE_ID = "mi_fuente"

def ingest_mi_fuente(db_path=None):
    print(f"[1/1] Ingestando desde {SOURCE_ID}...")
    # Obtener datos
    registros = []
    # ... transformar ...
    query = "INSERT OR REPLACE INTO mi_tabla (...) VALUES (?, ?)"
    execute_many(query, registros, db_path)
    print(f"  -> {len(registros)} registros ingestados")

def run_full_ingestion(db_path=None):
    from database import init_database
    db = init_database(db_path)
    ingest_mi_fuente(db)
    return db

if __name__ == "__main__":
    run_full_ingestion()
```

---

## Módulo de Reportes

### Convención

Cada función de reporte:
1. Retorna un `pandas.DataFrame`
2. Usa `_df_from_query()` para conversión SQL → DataFrame
3. Acepta un parámetro opcional `db_path`
4. Tiene un nombre descriptivo: `report_<qué>_<filtro>()`

### Ejemplo de Reporte

```python
def report_jugadores_por_tarjetas(min_tarjetas: int = 2, db_path: str = None) -> pd.DataFrame:
    query = """
        SELECT player_name, team_name, yellow_cards, red_cards, cards_per_90
        FROM players
        WHERE (yellow_cards + red_cards) >= ?
        ORDER BY cards_per_90 DESC
    """
    return _df_from_query(query, (min_tarjetas,), db_path)
```

### Agregar un Reporte a la TUI

1. Crea la función de reporte en `reports.py`.
2. Agrega un `ReportScreen` en `tui_app.py`:

```python
def action_show_mi_reporte(self) -> None:
    self.app.push_screen(ReportScreen("Mi Reporte", report_jugadores_por_tarjetas(3)))
```

3. Agrega un atajo de teclado en `MainScreen.BINDINGS`:

```python
Binding("m", "show_mi_reporte", "Mi Reporte"),
```

4. Agrega un ítem de menú en `MainScreen.compose()`:

```python
yield Static("[b]m[/b]  Mi Reporte", classes="menu-item")
```

---

## Utilidades de Apuestas

Todas las utilidades de apuestas son **funciones puras** (sin acceso a base de datos, sin efectos secundarios). Esto las hace testeables y reutilizables en CLI, TUI y notebooks.

### Conversión de Probabilidades

```python
from betting_utils import parse_odds

odds = parse_odds("+150")
print(odds.decimal)        # 2.500
print(odds.american)       # 150
print(odds.implied_prob)   # 0.400
```

### Criterio de Kelly

```python
from betting_utils import kelly_criterion

stake_pct, recommendation = kelly_criterion(
    model_prob=0.45,      # Tu probabilidad estimada
    odds_decimal=2.20,    # Probabilidades decimales ofrecidas
    fraction=0.25         # Kelly fraccional (conservador)
)
# Retorna: (0.0156, "Marginal edge—bet 1.56% of bankroll or pass")
```

### Agregar una Nueva Calculadora

1. Agrega la función a `betting_utils.py`.
2. Agrega comando CLI en `cli.py`:

```python
def cmd_mi_calc(args):
    result = mi_calculo(args.param1, args.param2)
    print(f"Resultado: {result}")

# En main():
p_calc = subparsers.add_parser("micalc", help="Mi nueva calculadora")
p_calc.add_argument("--param1", type=float, required=True)
p_calc.set_defaults(func=cmd_mi_calc)
```

---

## Desarrollo de la TUI

### Framework Textual

La TUI usa [Textual](https://textual.textualize.io/), un framework moderno de Python para aplicaciones de terminal.

### Tipos de Pantalla

| Pantalla | Uso |
|:---|:---|
| `ReportScreen` | Cualquier DataFrame de pandas |
| `PlayerDetailScreen` | Perfil completo de jugador (renderizado Markdown) |
| `SearchScreen` | Input + tabla de resultados |
| `VenueScreen` | Tabla de datos de sedes |
| `MarkdownReportScreen` | Contenido Markdown estático |

### Estilos CSS

Textual usa su propia sintaxis tipo CSS. El CSS a nivel de aplicación está en `SBFG2026TUI.CSS`:

```python
CSS = """
Screen { align: center middle; }
.report-header { height: 1; background: $primary-darken-2; ... }
DataTable { height: 1fr; border: solid $primary; }
"""
```

Para estilos específicos de pantalla, usa el atributo de clase `CSS` en la clase de pantalla.

### Ejecutar la TUI en Modo Desarrollo

Textual tiene una consola de desarrollador integrada:

```bash
textual run --dev src/tui_app.py
```

Esto abre una ventana de consola separada con inspector DOM y recarga CSS en caliente.

---

## Desarrollo de la CLI

### Agregar un Nuevo Comando

1. Escribe la función manejadora:

```python
def cmd_mi_comando(args):
    df = report_mi_reporte(args.limit)
    print(tabulate(df, headers="keys", tablefmt="grid", showindex=False))
```

2. Registra el subparser:

```python
p = subparsers.add_parser("micomando", help="Descripción")
p.add_argument("--limit", type=int, default=20)
p.set_defaults(func=cmd_mi_comando)
```

3. Prueba:

```bash
.venv/bin/python src/cli.py micomando --limit 10
```

---

## Pruebas y Validación

### Validación Manual

```bash
make test          # Validación básica de import + conteos
make build-db      # Prueba de pipeline completo
python src/cli.py counts   # Verificar todas las tablas pobladas
```

### Verificaciones de Calidad de Datos

Ejecuta estas consultas después de cualquier ingesta:

```sql
-- Jugadores con minutos pero sin goles (debe haber muchos)
SELECT COUNT(*) FROM players WHERE minutes_played > 0;

-- Jugadores con xG pero sin goles (sub-rendimiento)
SELECT player_name, goals, xg FROM players WHERE xg > 2 AND goals = 0;

-- Partidos sin eventos (debe ser 0)
SELECT COUNT(*) FROM matches m WHERE NOT EXISTS (
    SELECT 1 FROM match_events e WHERE e.match_id = m.match_id
);
```

---

## Lista de Verificación de Lanzamiento

Antes de hacer push a git o lanzar:

- [ ] `make test` pasa
- [ ] `make build-db` completa sin errores
- [ ] `make reports` genera los 16 archivos CSV
- [ ] `./tui.sh` lanza y todas las pantallas navegan correctamente
- [ ] `src/cli.py counts` muestra los conteos esperados
- [ ] README está actualizado
- [ ] DEVELOPER_GUIDE refleja la arquitectura actual
- [ ] `.gitignore` excluye `data/*.db`, `reports/*.csv`, `.venv/`
- [ ] `pyproject.toml` versión actualizada si aplica
- [ ] No hay rutas hardcodeadas ni claves de API en el código fuente

---

## Problemas Comunes

### "Database is locked"

SQLite no soporta escrituras concurrentes. Cierra la TUI o cualquier otra conexión antes de ejecutar ingesta.

### La TUI se ve distorsionada en terminal

Asegúrate de que tu terminal soporte Unicode y tenga al menos 80×24 caracteres. Para mejores resultados, usa un terminal moderno (iTerm2, Windows Terminal, GNOME Terminal, Alacritty).

---

## Contribuir

1. Haz fork del repositorio
2. Crea una rama de feature: `git checkout -b feature/mi-feature`
3. Realiza tus cambios
4. Ejecuta la lista de verificación de lanzamiento
5. Envía un pull request

Para preguntas, abre un issue o contacta a los mantenedores.

---

*Última actualización: 2026-05-05*
