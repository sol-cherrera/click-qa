# ClickQA

Herramienta de escritorio para documentar planes de prueba manuales. Captura pantallas con un **resaltado en forma de puntero** en la posición del ratón al momento de la captura, en **cualquier ventana** (multi-monitor).

## Cómo funciona

- Atajo global **Mayús + S** (`Shift+S`): toma la captura usando la posición actual del puntero como punto del highlight. **El clic del ratón no dispara captura** (evita capturas accidentales).
- **Exportación a Excel**: hoja nueva en un `.xlsx` existente, con imágenes embebidas a **alta resolución** (hasta 1920 px de ancho) para poder ampliar con buen detalle.
- En el **dashboard** puedes **eliminar** pasos capturados por error, editar el highlight y ver la captura a **tamaño nativo** (con desplazamiento).

---

## Instalación

> **Requisitos**: Python 3.10 o superior (recomendado 3.11+)

### 1. Crear entorno virtual (recomendado)

En la carpeta del proyecto (`click-qa`):

```bash
python -m venv .venv
```

### 2. Activar el entorno virtual

**Windows (PowerShell o CMD):**

```bash
.venv\Scripts\activate
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

Cuando el entorno esté activo verás `(venv)` al inicio del prompt.

### 3. Instalar dependencias

Con el entorno virtual activado:

```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación

```bash
python main.py
```

En **macOS**, para atajos globales y captura de pantalla puede ser necesario conceder permisos de **accesibilidad** y **grabación de pantalla** a Terminal o al intérprete Python que uses.

---

## Uso

### Panel de control (ventana pequeña, siempre encima)

| Acción | Cómo |
|--------|------|
| **Iniciar grabación** | Botón "Iniciar Grabacion" |
| **Capturar un paso** | Coloca el puntero donde quieras señalar y pulsa **Mayús + S** |
| **Pausar** | Botón "Pausar" (solo visible mientras grabas) |
| **Reanudar** | Botón "Reanudar" (cuando está pausado) |
| **Detener** | Botón "Detener y Revisar" — abre el dashboard |
| **Dashboard** | Botón "Dashboard →" (también durante la grabación) |

Las capturas **no** se toman al hacer clic; solo con **Mayús + S**. El panel y el dashboard se excluyen: si el puntero está sobre ellos, no se captura.

### Región de captura (opcional)

Puedes limitar la captura a un rectángulo de pantalla con **Seleccionar region** en el panel.

### Dashboard

- **Eliminar**: botón "Eliminar" en cada tarjeta (con confirmación).
- **Exportar a Excel**: elige el archivo `.xlsx`, indica el **nombre de la hoja** (o déjalo en blanco para un nombre automático) y confirma.

---

## Estructura del proyecto

```
click-qa/
├── main.py                 ← Punto de entrada
├── requirements.txt
├── README.md
├── assets/
│   └── solutoria-logo-wfondo.png
├── src/
│   ├── paths.py            ← Rutas de recursos (logo)
│   ├── recorder.py         ← Motor: pynput + mss + Pillow
│   ├── step_manager.py     ← Pasos en memoria
│   ├── ui/
│   │   ├── styles.py
│   │   ├── main_window.py
│   │   ├── dashboard_window.py
│   │   ├── step_widget.py
│   │   ├── highlight_editor.py
│   │   └── region_selector.py
│   └── exporters/
│       ├── excel_exporter.py
│       ├── pdf_exporter.py
│       └── docx_exporter.py
```

---

## Ejecutable (Windows)

Con el entorno activado e instaladas las dependencias de build:

```bash
pip install -r requirements-build.txt
pyinstaller --noconfirm ClickQA.spec
```

El archivo queda en `dist/ClickQA.exe`. Para tenerlo en Inicio y/o en Escritorio, hacer clic derecho para seleccionar `Anclar a Inicio` o `Enviar` -> `Escritorio (Acceso Directo)`. 
---

## Notas

- Los pasos se guardan **en memoria** durante la sesión. Al cerrar la app se pierden (exporta antes de cerrar).
- Varios monitores: la captura usa el monitor que contiene el puntero (o la región definida).
- **Excel abierto**: si el `.xlsx` está abierto en Excel, la app puede usar **xlwings** para insertar la hoja y guardar sin error de permisos.
