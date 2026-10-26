# NARVAL MVP — SISTEMA IOT DE MONITOREO DE CALIDAD DEL AGUA

Narval es un sistema IoT de adquisición, persistencia, evaluación determinista e interpretación inteligente de parámetros seleccionados de calidad del agua (**pH, turbidez y temperatura**), orientado al contexto de acueductos rurales en Colombia.

El sistema combina:
1. **Hardware & Firmware:** ESP32 con MicroPython leyendo electrodo de pH, sensor óptico de turbidez y sonda digital DS18B20 (OneWire).
2. **Backend API:** FastAPI (Python 3.11+) con arquitectura en capas limpia y persistencia mediante SQLAlchemy 2.
3. **Base de Datos:** PostgreSQL alojado en Supabase (o PostgreSQL local), con control de versiones de esquema mediante migraciones de Alembic.
4. **Semáforo Virtual (Frontend):** Interfaz web en React 19 + TypeScript (Vite) con clasificación visual y textual basada en la **Resolución 2115 de 2007** de Colombia.
5. **Inteligencia Artificial:** Google Gemini (vía SDK oficial `google-genai` en el backend) para análisis descriptivo y contextual sobre mediciones reales persistidas.

> **AVISO TÉCNICO NORMATIVO:** Narval **NO** certifica potabilidad del agua ni reemplaza análisis de laboratorio de acueductos acreditados. El Semáforo Virtual refleja el comportamiento de los parámetros monitorizados contra referencias técnicas documentadas.

---

## 1. Estructura del Repositorio

```
Narval/
├── .env.example                 # Plantilla unificada de variables de entorno
├── .gitignore                   # Exclusión de credenciales, entornos y cachés
├── docs/                        # Fuente de verdad y documentación técnica oficial
│   ├── NARVAL_SOURCE_OF_TRUTH.md # Especificación maestra y control de alcance
│   ├── ARCHITECTURE.md          # Arquitectura en capas del backend y frontend
│   ├── DATABASE.md              # Modelo relacional, entidades y migraciones
│   ├── API.md                   # Contrato de endpoints REST de FastAPI
│   ├── HARDWARE.md              # Conexiones eléctricas, pinout y ADC del ESP32
│   ├── CALIBRATION.md           # Procedimientos metrológicos de calibración
│   ├── AI_INTEGRATION.md        # Integración segura de Google Gemini
│   ├── TESTING.md               # Resultados y reporte de pruebas automatizadas
│   └── STATUS.md                # Matriz de estado de requisitos del MVP
│
├── narval-backend/              # Backend en FastAPI con arquitectura en capas
│   ├── app/
│   │   ├── api/                 # Controladores y rutas REST (v1 y health)
│   │   ├── core/                # Configuración (.env), DB pooler y seguridad
│   │   ├── models/              # Modelos declarativos SQLAlchemy 2.0
│   │   ├── repositories/        # Capa de abstracción de acceso a datos
│   │   ├── schemas/             # DTOs y validadores Pydantic
│   │   └── services/            # Lógica de negocio (Semáforo Virtual, Gemini)
│   ├── alembic/                 # Migraciones de base de datos Alembic
│   ├── tests/                   # Suite de pruebas automatizadas con pytest (18 tests)
│   ├── requirements.txt         # Dependencias de Python
│   └── .env.example             # Plantilla de variables para el backend
│
├── narval-frontend/             # Semáforo Virtual en React + TypeScript (Vite)
│   ├── src/
│   │   ├── presentation/        # Componentes UI (Semáforo, Métricas, Historial, Gráficos, IA)
│   │   ├── hooks/               # Custom hooks (useMeasurements, useDeviceStatus, useAIAnalysis)
│   │   ├── services/            # Cliente API tipado
│   │   └── types/               # Tipos de dominio y DTOs
│   ├── .env.example             # Plantilla de variables para el frontend
│   └── package.json
│
└── firmware/                    # Firmware MicroPython para microcontrolador ESP32
    ├── boot.py                  # Arranque del microcontrolador y memoria
    ├── main.py                  # Bucle continuo de adquisición y envío HTTP
    ├── config.example.py        # Plantilla de configuración (Wi-Fi, URL, pines)
    ├── sensors/                 # Drivers de hardware (pH ADC1, Turbidez ADC1, OneWire)
    └── net/                     # Conector Wi-Fi y cliente HTTP con autenticación de token
```

---

## 2. Puesta en Marcha Rápida

### 2.1. Backend (FastAPI)

1. **Ingresar al directorio del backend:**
   ```bash
   cd narval-backend
   ```

2. **Crear y activar el entorno virtual:**
   - **En Windows:**
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\activate
     ```
   - **En Linux / macOS:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno:**
   Copia el archivo de plantilla `.env.example` a `.env`:
   - **En Windows:**
     ```powershell
     copy .env.example .env
     ```
   - **En Linux / macOS:**
     ```bash
     cp .env.example .env
     ```
   Abre `.env` y configura tus credenciales de PostgreSQL / Supabase, y opcionalmente tu `GEMINI_API_KEY`.

5. **Ejecutar migraciones y sembrado normativo:**
   ```bash
   alembic upgrade head
   python -m app.core.seed
   ```

6. **Iniciar el servidor de desarrollo:**
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

7. **Acceder a la documentación Swagger interactiva:**
   - Swagger UI: 👉 `http://localhost:8000/docs`
   - Health check: 👉 `http://localhost:8000/health`

---

### 2.2. Frontend (Semáforo Virtual)

1. **En una nueva terminal, ingresar al directorio del frontend:**
   ```bash
   cd narval-frontend
   ```

2. **Instalar dependencias de Node:**
   ```bash
   npm install
   ```

3. **(Opcional) Configurar variables de entorno:**
   Por defecto, el frontend se conecta a `http://localhost:8000`. Si deseas cambiar la URL del API:
   ```bash
   # Windows:
   copy .env.example .env
   # Linux / macOS:
   cp .env.example .env
   ```

4. **Iniciar el servidor de desarrollo de Vite:**
   ```bash
   npm run dev
   ```

5. **Abrir en el navegador:**  
   👉 `http://localhost:5173`

---

### 2.3. Configuración de Google Gemini

1. Obtén tu clave gratuita de API en [Google AI Studio](https://aistudio.google.com/).
2. Ábrela y pégala en `narval-backend/.env`:
   ```env
   GEMINI_API_KEY="AIzaSyTuClaveAqui..."
   GEMINI_MODEL="gemini-2.5-flash"
   ```
3. Reinicia el backend. Al pulsar el botón **"Generar Análisis IA"** en la interfaz web, el sistema enviará los datos físicos persistidos al modelo Gemini.
4. **Modo Contingencia:** Si no configuras la clave (`GEMINI_API_KEY=""`), el backend activará automáticamente su generador determinista local de respaldo sin interrumpir la operación ni arrojar errores al usuario.

---

### 2.4. Firmware en ESP32 (MicroPython)

1. Ingresa a la carpeta `firmware/` y copia la plantilla de configuración:
   ```bash
   cd firmware
   # Windows:
   copy config.example.py config.py
   # Linux / macOS:
   cp config.example.py config.py
   ```
2. Edita `firmware/config.py` con tu red Wi-Fi y la dirección de tu backend:
   ```python
   WIFI_SSID = "MiWiFi"
   WIFI_PASSWORD = "MiPassword"
   BACKEND_URL = "http://192.168.1.100:8000/api/v1/measurements"
   DEVICE_TOKEN = "narval-esp32-secret-2026"  # Debe coincidir con DEVICE_INGESTION_SECRET del backend
   ```
3. Sube los archivos a tu ESP32 con [Thonny IDE](https://thonny.org/) o mediante `mpremote`:
   ```bash
   pip install mpremote
   mpremote connect COM3 cp -r . :
   ```
4. Reinicia el ESP32. El dispositivo conectará a la red Wi-Fi y transmitirá las lecturas de los sensores al backend cada 10 segundos.

---

## 3. Ejecución de Pruebas Automatizadas

```bash
# Pruebas del Backend (18 tests unitarios y de integración)
cd narval-backend
pytest -v

# Compilación y verificación estricta de tipos de TypeScript en el Frontend
cd ../narval-frontend
npm run build
```

---

## 4. Licencia y Atribución

Desarrollado para el proyecto **Narval** — Sistema de monitoreo de calidad del agua en acueductos rurales colombianos.
Normativa de referencia: **Resolución 2115 de 2007** (Ministerio de la Protección Social y Ministerio de Ambiente, Vivienda y Desarrollo Territorial de la República de Colombia).
