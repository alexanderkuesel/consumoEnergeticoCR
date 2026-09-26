# data/analysis

Consolida los datos crudos de `raw/` en DataFrames de pandas, con índice
horario continuo (`fecha_hora`, hora local de Costa Rica).

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

Desde la raíz del repo:

```python
from data.analysis.consolidate import build_hourly, load_demanda, load_weather_by_city

df = build_hourly()                 # demanda + clima ponderado + calendario
df = build_hourly(by_city=True)     # + temperatura/humedad/punto de rocío por ciudad
ciudades = load_weather_by_city()   # formato largo, índice (fecha_hora, city)
```

O generar `data/analysis/hourly.parquet` (ignorado por git, se regenera):

```bash
python -m data.analysis.consolidate
```

## Funciones

| Función | Fuente | Columnas |
|---|---|---|
| `load_demanda()` | `raw/cence_consumo/demanda_mw.csv` | `mw`, `mw_programada` |
| `load_weather_weighted()` | `raw/weather/weather_weighted.csv` | `temperature_2m_wavg`, `relative_humidity_2m_wavg`, `dew_point_2m_wavg`, `n_cities` |
| `load_weather_by_city(wide=False)` | `raw/weather/weather_by_city.csv` | `temperature_2m`, `relative_humidity_2m`, `dew_point_2m` (por ciudad) |
| `build_hourly(by_city=False, calendar=True)` | todas | las anteriores + `anio`, `mes`, `dia_semana`, `hora`, `fin_de_semana` |

## Notas sobre los datos

- Rango de demanda: 2012-03-01 a 2026-09-25, sin horas faltantes; 23 horas con `mw` vacío.
- El clima termina el 2026-09-18, por lo que la última semana queda en NaN tras el join.
- `apparent_temperature` viene vacía en la fuente y se descarta.
- Hay valores de `mw` anómalamente bajos (mínimo ~129 MW, probablemente apagones o
  errores de registro); no se filtran aquí, revisarlos antes de modelar.
