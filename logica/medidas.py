# Medidas administrativas. Las hojas llegan ya cargadas en H2.
# Sin conexiones: main.py escribe <esquema>.DW_MED_*.

RESULTADO = pd.DataFrame(
    [
        {"TABLA": "DW_MED_SUSC_INFO_GENERAL", "FILAS": len(SUSC_INFO_GENERAL)},
        {"TABLA": "DW_MED_SUSC_PROCESO_PREVIO", "FILAS": len(SUSC_PROCESO_PREVIO)},
        {"TABLA": "DW_MED_SUSC_ETAPAS_MA", "FILAS": len(SUSC_ETAPAS_MA)},
        {"TABLA": "DW_MED_SUSC_MA_GABINETE", "FILAS": len(SUSC_MA_GABINETE)},
        {"TABLA": "DW_MED_SUSC_MA_CAMPO", "FILAS": len(SUSC_MA_CAMPO)},
        {"TABLA": "DW_MED_SEG_LISTA_MA", "FILAS": len(SEG_LISTA_MA)},
        {"TABLA": "DW_MED_SEG_UBICACION", "FILAS": len(SEG_UBICACION)},
        {"TABLA": "DW_MED_SEG_INFO_ADICIONAL", "FILAS": len(SEG_INFO_ADICIONAL)},
        {"TABLA": "DW_MED_SEG_MEDIDAS", "FILAS": len(SEG_MEDIDAS)},
        {"TABLA": "DW_MED_SEG_ACREDITACION", "FILAS": len(SEG_ACREDITACION)},
        {"TABLA": "DW_MED_SEG_MODIFICATORIAS", "FILAS": len(SEG_MODIFICATORIAS)},
    ]
)
