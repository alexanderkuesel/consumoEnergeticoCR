"""Carga y consolida los datos crudos en DataFrames de pandas.

Uso como módulo (desde la raíz del repo):

    from data.analysis.consolidate import build_hourly
    df = build_hourly()

Uso como script (escribe data/analysis/hourly.parquet):

    python -m data.analysis.consolidate

Todas las marcas de tiempo están en hora local de Costa Rica (UTC-6, sin
horario de verano), tanto en CENCE como en ERA5-Land (Open-Meteo con
timezone=America/Costa_Rica), por lo que se unen directamente.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = REPO_ROOT / "raw"
OUTPUT_PATH = Path(__file__).resolve().parent / "hourly.parquet"

WEATHER_VARS = ["temperature_2m", "relative_humidity_2m", "dew_point_2m"]


def _hourly_index(index: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """Índice horario continuo entre el primer y último registro."""
    return pd.date_range(index.min(), index.max(), freq="h", name="fecha_hora")


def load_demanda(raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    """Demanda horaria del SEN (CENCE / DOCSE-ICE).

    Columnas:
        mw            demanda real (MW, valor instantáneo)
        mw_programada demanda programada/pronosticada (MW)
    """
    df = pd.read_csv(raw_dir / "cence_consumo" / "demanda_mw.csv")
    df = df.rename(columns={"fechaHora": "fecha_hora", "MW": "mw", "MW_P": "mw_programada"})
    df["fecha_hora"] = pd.to_datetime(df["fecha_hora"])
    df = (
        df.drop_duplicates("fecha_hora", keep="last")
        .set_index("fecha_hora")
        .sort_index()
    )
    return df.reindex(_hourly_index(df.index))


def load_weather_weighted(raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    """Clima horario nacional, promedio ponderado por población (ERA5-Land).

    Se descarta `apparent_temperature`, que viene vacía en la fuente.
    """
    df = pd.read_csv(raw_dir / "weather" / "weather_weighted.csv", parse_dates=["fecha_hora"])
    df = df.drop(columns=["apparent_temperature_wavg"], errors="ignore")
    df = (
        df.drop_duplicates("fecha_hora", keep="last")
        .set_index("fecha_hora")
        .sort_index()
    )
    return df.reindex(_hourly_index(df.index))


def load_weather_by_city(raw_dir: Path = RAW_DIR, wide: bool = False) -> pd.DataFrame:
    """Clima horario por ciudad (ERA5-Land).

    wide=False: formato largo, índice (fecha_hora, city).
    wide=True:  una columna por variable y ciudad, e.g. `temperature_2m_liberia`.
    """
    df = pd.read_csv(raw_dir / "weather" / "weather_by_city.csv", parse_dates=["fecha_hora"])
    df = df.drop(columns=["apparent_temperature"], errors="ignore")
    df = df.drop_duplicates(["fecha_hora", "city"], keep="last")
    if not wide:
        return df.set_index(["fecha_hora", "city"]).sort_index()

    df = df.pivot(index="fecha_hora", columns="city", values=WEATHER_VARS)
    df.columns = [f"{var}_{city}" for var, city in df.columns]
    return df.sort_index()


def add_calendar_features(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega variables de calendario a partir del índice horario."""
    idx = df.index
    return df.assign(
        anio=idx.year,
        mes=idx.month,
        dia_semana=idx.dayofweek,  # 0 = lunes
        hora=idx.hour,
        fin_de_semana=idx.dayofweek >= 5,
    )


def build_hourly(
    raw_dir: Path = RAW_DIR,
    by_city: bool = False,
    calendar: bool = True,
) -> pd.DataFrame:
    """DataFrame horario consolidado: demanda + clima (+ calendario).

    El rango es el de la demanda; las horas sin datos de clima quedan en NaN.
    Con by_city=True se agregan las variables climáticas de cada ciudad.
    """
    df = load_demanda(raw_dir).join(load_weather_weighted(raw_dir), how="left")
    if by_city:
        df = df.join(load_weather_by_city(raw_dir, wide=True), how="left")
    if calendar:
        df = add_calendar_features(df)
    return df


def main() -> None:
    df = build_hourly(by_city=True)
    df.to_parquet(OUTPUT_PATH)
    print(f"{len(df):,} filas x {df.shape[1]} columnas -> {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    print(f"Rango: {df.index.min()} a {df.index.max()}")
    print("Valores faltantes:")
    print(df.isna().sum()[lambda s: s > 0].to_string())


if __name__ == "__main__":
    main()
