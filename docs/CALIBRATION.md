# CALIBRACIÓN Y VALIDACIÓN METROLÓGICA — PROYECTO NARVAL

## 1. Principio Fundamental
**No se inventan constantes ni curvas de conversión analógica.**  
Un sensor sin procedimiento de calibración verificado se clasifica como `calibration_status='PENDING'`, reportando su valor analógico bruto (`raw`) y su voltaje estimado (`voltage`), pero sin emitir un valor en unidades físicas definitivas si esto induce a error.

---

## 2. Procedimiento para el Sensor de pH
1. **Soluciones Buffer Estándar:**
   - Buffer pH 7.00 (neutralidad).
   - Buffer pH 4.01 (acidez).
2. **Método de Calibración:**
   - Sumergir el electrodo en solución buffer 7.00 a 25 °C. Registrar voltaje $V_7$.
   - Enjuagar con agua destilada y sumergir en solución buffer 4.01. Registrar voltaje $V_4$.
   - Pendiente (Slope): $m = \frac{7.00 - 4.01}{V_7 - V_4}$.
   - Intercepto: $b = 7.00 - m \cdot V_7$.
   - Ecuación de conversión: $\text{pH} = m \cdot V + b$.
3. **Estado Actual en Narval:**
   - Mientras no se suministren los buffers y se ejecute el procedimiento, el firmware reporta el voltaje y el backend evalúa el estado como `PENDING`.

---

## 3. Procedimiento para el Sensor de Turbidez
1. **Comportamiento Óptico:**
   - En agua limpia (0 NTU), la luz del emisor infrarrojo llega casi sin atenuación al fototransistor $\rightarrow$ Voltaje alto (ej. 4.0V - 4.5V).
   - A mayor turbidez (más partículas), la dispersión lumínica atenúa la señal $\rightarrow$ El voltaje decrece.
2. **Validación:**
   - No se utiliza la típica fórmula polinómica genérica de internet sin contrastar con patrones de Formazina en laboratorio, pues cada módulo chino tiene ganancias de potenciómetro y ópticas variables.
   - En ausencia de calibración experimental, el sistema reporta el voltaje y marca el estado como `PENDING`.
