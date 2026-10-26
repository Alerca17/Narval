# MODELO DE BASE DE DATOS Y PERSISTENCIA — PROYECTO NARVAL

## 1. Conexión a PostgreSQL en Supabase

Supabase provee dos modalidades de conexión:
1. **Transaction Pooler (Puerto 6543):** Recomendado para alta concurrencia de consultas de aplicación en backend serverless o contenedores.
2. **Session / Direct Pooler (Puerto 5432):** Necesario para migraciones DDL con Alembic y operaciones que requieren estado de sesión.

### Cadena de Conexión en SQLAlchemy 2
En Python utilizamos el driver moderno `psycopg` (versión 3):
- Aplicación: `postgresql+psycopg://postgres.guutvfsyawucvvsifaoe:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:5432/postgres` (o 6543)
- Migraciones Alembic: `postgresql+psycopg://postgres.guutvfsyawucvvsifaoe:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:5432/postgres`

---

## 2. Diagrama Entidad-Relación

```mermaid
erDiagram
    DEVICES ||--o{ MEASUREMENTS : "emite"
    MEASUREMENTS ||--o{ ALERTS : "genera"
    MEASUREMENTS ||--o{ AI_ANALYSES : "analizada_en"
    
    DEVICES {
        int id PK
        string code UK
        string name
        string status
        string api_key_hash
        string firmware_version
        datetime last_seen_at
        datetime created_at
    }

    MEASUREMENTS {
        int id PK
        int device_id FK
        string packet_id UK
        float ph_raw
        float ph_voltage
        float ph_value
        float turbidity_raw
        float turbidity_voltage
        float turbidity_value
        float temperature_celsius
        datetime device_timestamp
        datetime received_at
        string quality_status
        string calibration_status
        text validation_notes
    }

    ALERTS {
        int id PK
        int measurement_id FK
        string parameter_name
        float observed_value
        string threshold_reference
        string severity
        text message
        datetime created_at
    }

    AI_ANALYSES {
        int id PK
        int measurement_id FK
        string query_scope
        string model_used
        text analysis_text
        text summary
        text limitations_disclaimer
        datetime created_at
    }

    REFERENCE_RULES {
        int id PK
        string parameter_name
        string source
        float min_value
        float max_value
        string unit
        boolean is_active
        string version
    }

    SENSOR_CALIBRATIONS {
        int id PK
        string sensor_type
        datetime calibration_date
        json parameters_json
        text notes
        boolean is_active
    }
```

---

## 3. Especificación de Tablas

### 3.1. `devices`
- `id`: Clave primaria autoincremental (`SERIAL` / `BIGSERIAL`).
- `code`: Identificador unívoco del hardware (ej. `'ESP32-NARVAL-001'`).
- `name`: Nombre descriptivo legible (ej. `'Estación Rural Quebrada Alta'`).
- `status`: Estado operativo: `'ONLINE'`, `'OFFLINE'`, `'ERROR'`.
- `api_key_hash`: Hash SHA256 del token utilizado por el ESP32 para autenticar la ingestión.
- `firmware_version`: Versión del firmware reportada (ej. `'1.0.0-mp'`).
- `last_seen_at`: Timestamp de la última comunicación exitosa.
- `created_at`: Fecha de registro inicial.

### 3.2. `measurements`
- `id`: Clave primaria autoincremental.
- `device_id`: Clave foránea referenciando `devices(id)`.
- `packet_id`: Hash / UUID de paquete enviado por el microcontrolador para deduplicación idempotente.
- `ph_raw`: Valor analógico bruto (0 - 4095).
- `ph_voltage`: Voltaje calculado en voltios (V).
- `ph_value`: Valor de pH convertido (0.0 - 14.0), nulo si no hay calibración.
- `turbidity_raw`: Valor analógico bruto del sensor de turbidez.
- `turbidity_voltage`: Voltaje calculado (V).
- `turbidity_value`: Valor en NTU, nulo si no hay curva de calibración validada.
- `temperature_celsius`: Temperatura reportada por el sensor DS18B20 (°C).
- `device_timestamp`: Marca de tiempo reportada por el ESP32 (RTC o NTP).
- `received_at`: Marca de tiempo registrada por el servidor al momento de la ingesta.
- `quality_status`: `'VALID'` (todos los datos coherentes), `'PARTIAL'` (uno o más sensores sin calibrar o fallando), `'INVALID'` (lecturas fuera de rango físico o paquete corrupto).
- `calibration_status`: `'CALIBRATED'` (sensores con parámetros calibrados), `'PENDING'` (valores brutos sin calibración confirmada).
- `validation_notes`: Texto explicativo de anomalías o incidencias encontradas durante la validación.

### 3.3. `alerts`
- `id`: Clave primaria.
- `measurement_id`: Clave foránea opcional a `measurements(id)`.
- `parameter_name`: `'ph'`, `'turbidity'`, `'temperature'`, `'system'`.
- `observed_value`: Valor numérico detectado.
- `threshold_reference`: Texto del umbral violado (ej. `'pH < 6.5 (Res. 2115/2007)'`).
- `severity`: `'INFO'`, `'WARNING'`, `'CRITICAL'`.
- `message`: Explicación clara y determinista.
- `created_at`: Marca de tiempo.

### 3.4. `ai_analyses`
- `id`: Clave primaria.
- `measurement_id`: Clave foránea referenciando la medición analizada.
- `query_scope`: `'SINGLE'`, `'RECENT_BATCH'`.
- `model_used`: Identificador del modelo Gemini (ej. `'gemini-2.5-flash'`).
- `analysis_text`: Informe descriptivo generado por Gemini.
- `summary`: Resumen ejecutivo de 1-2 oraciones.
- `limitations_disclaimer`: Cláusula explícita de limitaciones del análisis.
- `created_at`: Marca de tiempo.

### 3.5. `reference_rules`
- Almacena los umbrales configurados para el semáforo virtual, vinculados formalmente a su fuente normativa (Resolución 2115 de 2007).
