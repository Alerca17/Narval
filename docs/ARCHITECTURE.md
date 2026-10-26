# ARQUITECTURA DEL SISTEMA — PROYECTO NARVAL

## 1. Visión General
Narval adopta una **Arquitectura en Capas Limpia (Clean Layered Architecture)** tanto en el Backend (FastAPI) como en el Frontend (React + TypeScript), garantizando separación de responsabilidades, alta testabilidad, desacoplamiento del framework respecto a la lógica de negocio y facilidad de mantenimiento.

```
┌─────────────────────────────────────────────────────────────┐
│                 ESP32 (MicroPython Firmware)                │
│  - Sensores: pH (ADC), Turbidez (ADC), DS18B20 (OneWire)    │
│  - Validador eléctrico local & Conversión calibrada         │
│  - Emisor HTTP/HTTPS (POST /api/v1/measurements)            │
└──────────────────────────────┬──────────────────────────────┘
                               │  JSON payload + X-Device-Token
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 FASTAPI BACKEND (Python 3.14)               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 1. API Layer (Routers & Request Handlers)             │  │
│  │    - /api/v1/measurements (Ingesta, Última, Historial)│  │
│  │    - /api/v1/devices (Estado y Comunicación)          │  │
│  │    - /api/v1/alerts (Alertas activas e históricas)    │  │
│  │    - /api/v1/ai (Análisis descriptivo contextual)     │  │
│  │    - /health (Chequeo de servicio y conectividad DB)  │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              │                              │
│  ┌───────────────────────────▼───────────────────────────┐  │
│  │ 2. Service Layer (Lógica de Negocio Pura)             │  │
│  │    - MeasurementService (Deduplicación & Validación)  │  │
│  │    - VirtualSemaforoEngine (Reglas deterministas)     │  │
│  │    - AIService (Integración con Google Gemini)        │  │
│  │    - DeviceService (Heartbeat y Estado operativo)     │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              │                              │
│  ┌───────────────────────────▼───────────────────────────┐  │
│  │ 3. Repository Layer (Acceso a Datos / Abstracción)    │  │
│  │    - MeasurementRepository, DeviceRepository, etc.   │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              │                              │
│  ┌───────────────────────────▼───────────────────────────┐  │
│  │ 4. Domain & Data Persistence Layer (SQLAlchemy 2.0)   │  │
│  │    - Modelos Declarativos Mapped[...]                 │  │
│  │    - Alembic Database Migrations                      │  │
│  └───────────────────────────┬───────────────────────────┘  │
└──────────────────────────────┼──────────────────────────────┘
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
┌─────────────────────────┐           ┌────────────────────────┐
│  PostgreSQL en Supabase │           │    Google Gemini API   │
│  - Pooler Transaccional │           │    (vía SDK oficial    │
│  - Conexión Directa     │           │     google-genai)      │
└─────────────────────────┘           └────────────────────────┘
            ▲
            │ HTTP REST (Backend proxy)
┌───────────┴─────────────────────────────────────────────────┐
│              FRONTEND (React + TypeScript + Vite)           │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Presentation Layer (Componentes UI & Semáforo Virtual)│  │
│  │ - Semáforo Virtual, Tarjetas Métricas, Histórico      │  │
│  └───────────────────────────┬───────────────────────────┘  │
│  ┌───────────────────────────▼───────────────────────────┐  │
│  │ State & Hooks Layer (useMeasurements, useAIAnalysis)  │  │
│  └───────────────────────────┬───────────────────────────┘  │
│  ┌───────────────────────────▼───────────────────────────┐  │
│  │ Services Layer (ApiClient & DTO Mappers)              │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Capas del Backend
1. **API / Presentation (`app/api/`):** Define los endpoints REST, deserializa las peticiones con Pydantic, maneja códigos de estado HTTP y documenta automáticamente OpenAPI/Swagger.
2. **Service / Business Logic (`app/services/`):** Contiene las reglas del negocio:
   - Evaluación determinista del Semáforo Virtual según umbrales (Resolución 2115/2007).
   - Deduplicación de paquetes provenientes del microcontrolador.
   - Evaluación de calidad de datos (`VALID`, `PARTIAL`, `INVALID`).
   - Generación de contexto sanitizado para Gemini.
3. **Repository / Data Access (`app/repositories/`):** Aísla las consultas directas de SQLAlchemy 2, facilitando pruebas unitarias mediante mocks sin necesidad de tocar la base de datos física.
4. **Domain & Data (`app/domain/` / `app/models/`):** Clases de entidad SQLAlchemy 2 (`Mapped` y `mapped_column`) que mapean las tablas en PostgreSQL.
5. **Core (`app/core/`):** Configuración de entorno con `pydantic-settings`, ciclo de vida del motor de base de datos (`engine`, `sessionmaker`), seguridad y logging centralizado.

---

## 3. Capas del Frontend
1. **Presentation (`src/presentation/`):** Componentes React puros que reciben `props` y renderizan la interfaz:
   - `SemaforoVirtual`: Visualizador visual y textual del estado general y por parámetro.
   - `MetricCards`: Tarjetas individuales para pH, Turbidez y Temperatura.
   - `HistoryTable`: Tabla con paginación, filtros de fecha y estado de validación.
   - `MetricCharts`: Gráficas temporales con líneas de umbral normativo.
   - `AIAnalysisCard`: Visualización del informe descriptivo emitido por Gemini.
2. **Custom Hooks (`src/hooks/`):** Gestión reactiva del ciclo de vida de los datos (`useMeasurements`, `useDeviceStatus`, `useAIAnalysis`), desacoplando la lógica de fetching de la vista.
3. **Services (`src/services/`):** Funciones de llamada HTTP (`fetch` / `axios` tipado) hacia el backend FastAPI.
4. **Types / Domain (`src/types/`):** Interfaces TypeScript que reflejan los DTOs del backend.
