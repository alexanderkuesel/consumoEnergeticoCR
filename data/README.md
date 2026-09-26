# Data

## cence_demand.csv
Datos de demanda energética por hora, tomados directamente del DOCSE-ICE. 

## weather_weighted.csv
Datos ambientales recogidos de ERA5-LAND. ERA5-Land tiene espaciado de 0.1 grados (~9km), que permite mas granularidad. Cada provincia tiene condiciones climáticas diferentes, por lo que se hizo un query por separado de cada uno, y se consolidaron los datos usando una modificador (weighted average) que considera la población de cada una. 

Nota: es posible ser mas meticuloso aqui, ya que los usos energéticos difieren en el GAM al de las costas, especialmente en uso de A/C. También sería interesante analizar por regiones socio-económicas, donde se espera que el consumo energético va en linea con ingresos (e.g. Escazú consume mas por m2 que Alajuelita).

- Los valores por hora son instantaneos, no agregados
