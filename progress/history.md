# Bitácora harness (append-only)

---

## Plantilla

Al cerrar una feature, append aquí: fecha, id, resumen, evidencia (`progress/impl_<id>.md`).

---

## 2026-10-04 — fase-1-entorno, fase-2-fuentes, fase-3-oracle

Sheets de 20 libros a 11 tablas `APP.DW_MED_*`. Dos pasos de carga (`suscripcion`, `seguimiento`). `./init.sh` terminó en `HARNESS OK`. Evidencia: `progress/impl_fase-1-entorno.md`, `progress/impl_fase-2-fuentes.md`, `progress/impl_fase-3-oracle.md`. Windows pendiente: `init.bat remote`.

## 2026-10-04 — fase-4-od

31 libros de oficinas desconcentradas a 4 tablas `APP.DW_MED_OD_*`. Paso `cargar_sheets.py od` después de seguimiento. `./init.sh` terminó en `HARNESS OK`. Evidencia: `progress/impl_fase-4-od.md`. Cotabambas no aporta filas a modificatorias (pestaña vacía con códigos de acreditación). Windows pendiente: `init.bat remote`.

## 2026-10-07 — fase-5-mysql

Destino de las 15 tablas `DW_MED_*` y `DW_MED_OD_*` en MySQL `gappsdb` (`localhost:3307`). `./init.sh` terminó en `HARNESS OK`. Evidencia: `progress/impl_fase-5-mysql.md`. Windows pendiente: `init.bat remote` contra `10.1.1.217:3306/gappsdb`.
