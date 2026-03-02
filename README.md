# QA Step Recorder — Desktop

Herramienta de escritorio para automatizar la documentacion de planes de prueba manuales en **Windows**. Captura screenshots con el click resaltado en **cualquier ventana**.

## Como funciona

- Usa hooks globales del sistema operativo (`pynput`) para detectar clicks.
- Dibuja el cursor en las coordenadas exactas del clic con `Pillow`.
- Exporta en hoja nueva en archivo **Excel** seleccionado con imagenes embebidas.

---

## Instalacion

> **Requisitos**: Python 3.11 o superior

### 1. Crear entorno virtual (recomendado)

En la carpeta `QA/` ejecuta:

```bash
python -m venv venv
```

### 2. Activar el entorno virtual

**Windows (PowerShell o CMD):**
```bash
venv\Scripts\activate
```

**Linux / macOS:**
```bash
source venv/bin/activate
```

Cuando el entorno esté activo verás `(venv)` al inicio del prompt.

### 3. Instalar dependencias

Con el entorno virtual activado:

```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicacion

```bash
python main.py
```

---

## Uso

### Panel de control (ventana pequena, siempre encima)

| Accion | Como |
|--------|------|
| **Iniciar grabacion** | Click en "▶ Iniciar Grabacion" |
| **Pausar** | Click en "⏸ Pausar" durante la grabacion |
| **Reanudar** | Click en "▶ Reanudar" |
| **Detener** | Click en "⏹ Detener y Revisar" — abre el dashboard |
| **Dashboard directo** | Click en "📊 Dashboard" durante la grabacion |



## Estructura del proyecto

```
QA/
├── main.py                      ← Punto de entrada
├── requirements.txt             ← Dependencias Python
├── README.md
├── src/
│   ├── recorder.py              ← Motor: pynput + mss + Pillow
│   ├── step_manager.py          ← Gestion de pasos en memoria
│   └── ui/
│       ├── styles.py            ← Tema oscuro (QSS)
│       ├── main_window.py       ← Panel control (siempre encima)
│       ├── dashboard_window.py  ← Editor de pasos
│       └── step_widget.py       ← Tarjeta de paso individual
│   └── exporters/
│       ├── pdf_exporter.py      ← fpdf2
│       └── docx_exporter.py     ← python-docx
└── extension/                   ← Extension Chrome (version anterior)
```

---

## Notas

- Los pasos se guardan **en memoria** durante la sesion. Al cerrar la app se pierden (exporta antes de cerrar).
- Para paginas en otros monitores funciona correctamente con configuraciones multi-monitor.
- **Exportar a Excel abierto**: si el archivo .xlsx está abierto en Excel, la app usa automatización (xlwings) para añadir la hoja y guardar desde Excel, sin error de permisos.
