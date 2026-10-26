# NARVAL MVP — SISTEMA IOT DE MONITOREO DE CALIDAD DEL AGUA

Narval es un sistema IoT de adquisición, persistencia, evaluación determinista e interpretación inteligente de parámetros seleccionados de calidad del agua (**pH, turbidez y temperatura**), orientado al contexto de acueductos rurales en Colombia.

El sistema combina:
1. **Hardware & Firmware:** ESP32 con MicroPython leyendo electrodo de pH, sensor óptico de turbidez y sonda digital DS18B20 (OneWire).
2. **Backend API:** FastAPI (Python 3.14) con arquitectura en capas limpia y persistencia mediante SQLAlchemy 2.
3. **Base de Datos:** PostgreSQL alojado en Supabase, con control de versiones de esquema mediante migraciones de Alembic.
4. **Semáforo Virtual (Frontend):** Interfaz web en React + TypeScript (Vite) con clasificación visual y textual basada en la **Resolución 2115 de 2007** de Colombia.
5. **Inteligencia Artificial:** Google Gemini (vía SDK oficial `google-genai` en el backend) para análisis descriptivo y contextual sobre mediciones reales persistidas.

> **AVISO TÉCNICO NORMATIVO:** Narval **NO** certifica potabilidad del agua ni reemplaza análisis de laboratorio de acueductos acreditados. El Semáforo Virtual refleja el comportamiento de los parámetros monitorizados contra referencias técnicas documentadas.

---

## 1. Estructura del Repositorio

```
Narval/
├── docs/                        # Fuente de verdad y documentación técnica oficial
│   ├── NARVAL_SOURCE_OF_TRUTH.md # Especificación maestra y control de alcance
│   ├── ARCHITECTURE.md          # Arquitectura en capas del backend y frontend
│   ├── DATABASE.md              # Modelo relacional, entidades y migraciones
│   ├── API.md                   # Contrato de endpoints REST de FastAPI
│   ├── HARDWARE.md              # Conexiones eléctricas, pinout y ADC del ESP32
│   ├── CALIBRATION.md           # Procedimientos metrológicos de calibración
│   ├── AI_INTEGRATION.md        # Integración segura de Google Gemini
│   ├── TESTING.md               # Resultados de pruebas automatizadas
│   └── STATUS.md                # Matriz de estado de requisitos
│
├── narval-backend/              # Backend en FastAPI con arquitectura en capas
│   ├── app/
│   │   ├── api/                 # Controladores y rutas REST (v1 y health)
│   │   ├── core/                # Configuración (.env), DB pooler y seguridad
│   │   ├── models/              # Modelos declarativos SQLAlchemy 2.0
│   │   ├── repositories/        # Capa de abstracción de acceso a datos
│   │   ├── schemas/             # DTOs y validadores Pydantic
│   │   └── services/            # Lógica de negocio (Semáforo Virtual, Gemini)
│   ├── alembic/                 # Migraciones de base de datos
│   ├── tests/                   # Suite de pruebas automatizadas con pytest
│   ├── requirements.txt         # Dependencias de Python
│   └── .env                     # Variables de entorno y conexión a Supabase
│
├── narval-frontend/             # Semáforo Virtual en React + TypeScript (Vite)
│   ├── src/
│   │   ├── presentation/        # Componentes UI (Semáforo, Métricas, Historial, Gráficos, IA)
│   │   ├── hooks/               # Custom hooks (useMeasurements, useDeviceStatus, useAIAnalysis)
│   │   ├── services/            # Cliente API tipado
│   │   └── types/               # Tipos de dominio y DTOs
│   └── package.json
│
└── firmware/                    # Firmware MicroPython para microcontrolador ESP32
    ├── boot.py                  # Arranque del sistema
    ├── main.py                  # Ciclo continuo de adquisición y envío HTTP
    ├── config.py                # Configuración de Wi-Fi, pines y servidor
    ├── sensors/                 # Drivers para pH, Turbidez y DS18B20 OneWire
    └── net/                     # Gestor de Wi-Fi y cliente HTTP con deduplicación
```

---

## 2. Puesta en Marcha Rápida

### 2.1. Backend (FastAPI)

1. Abrir una terminal en `narval-backend/`:
   ```bash
   cd narval-backend
   ```
2. Activar el entorno virtual existente o crearlo:
   ```bash
   .\.venv\Scripts\activate
   ```
3. Ejecutar las migraciones de base de datos (ya sincronizadas con Supabase):
   ```bash
   alembic upgrade head
   ```
4. Iniciar el servidor de desarrollo:
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
5. Acceder a la documentación Swagger interactiva en:  
   👉 `http://localhost:8000/docs`  
   👉 `http://localhost:8000/health`

### 2.2. Frontend (Semáforo Virtual)

1. En una nueva terminal, ingresar a `narval-frontend/`:
   ```bash
   cd narval-frontend
   npm run dev
   ```
2. Abrir en el navegador:  
   👉 `http://localhost:5173`

### 2.3. Configuración de Google Gemini

1. Obtén tu clave gratuita en [Google AI Studio](https://aistudio.google.com/).
2. Ábrela y pégala en `narval-backend/.env`:
   ```env
   GEMINI_API_KEY="AIzaSyTuClaveAqui..."
   ```
3. Reinicia el backend. Ahora las solicitudes de análisis desde el botón de la interfaz utilizarán directamente el modelo `gemini-2.5-flash`. Si no configuras la clave, el sistema activará automáticamente su generador determinista local sin interrumpir el funcionamiento.

### 2.4. Firmware en ESP32

1. Abre `firmware/config.py` y coloca tu SSID y clave Wi-Fi, así como la IP local de tu computador:
   ```python
   WIFI_SSID = "MiWiFi"
   WIFI_PASSWORD = "Password123"
   BACKEND_URL = "http://192.168.1.100:8000/api/v1/measurements"
   ```
2. Sube los archivos a tu ESP32 con Thonny o `mpremote`:
   ```bash
   mpremote connect COM3 cp -r . :
   ```
3. Reinicia el ESP32 para comenzar a transmitir mediciones automáticamente.

---

## 3. Ejecución de Pruebas Automatizadas

```bash
# Pruebas del Backend (17 tests)
cd narval-backend
.\.venv\Scripts\python -m pytest -v

# Compilación y verificación de tipos del Frontend
cd narval-frontend
npm run build
```
