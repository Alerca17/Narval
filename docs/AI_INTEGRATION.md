# INTEGRACIÓN CON GOOGLE GEMINI — PROYECTO NARVAL

## 1. Arquitectura de Integración
La integración con Google Gemini se realiza exclusivamente a nivel de **Backend** mediante el SDK oficial `google-genai` (o API REST oficial de Google).

```
[ Frontend React ]
      │
      ▼ POST /api/v1/ai/analyze { measurement_id: 105 }
[ FastAPI Backend - AIService ]
      │ 1. Consulta la medición 105 y el historial en PostgreSQL
      │ 2. Sanitiza y estructura los datos reales y umbrales (Res. 2115/2007)
      │ 3. Inyecta el system prompt de restricciones científicas
      ▼
[ Google Gemini API (Model: gemini-2.5-flash) ]
      │ 4. Genera informe explicativo estructurado (JSON / texto)
      ▼
[ FastAPI Backend ]
      │ 5. Valida la respuesta y persiste en tabla `ai_analyses`
      ▼
[ Frontend React - Renderiza AIAnalysisCard ]
```

---

## 2. Instrucciones para Configurar la Clave de Gemini
1. Acceder a [Google AI Studio](https://aistudio.google.com/).
2. Iniciar sesión con una cuenta de Google y hacer clic en **"Get API key"** (Obtener clave de API).
3. Crear una nueva clave en un proyecto de Google Cloud (o el proyecto por defecto de AI Studio).
4. Copiar la clave generada (empieza usualmente por `AIzaSy...`).
5. Abrir el archivo `.env` en la raíz de `narval-backend/`:
   ```bash
   GEMINI_API_KEY="AIzaSyTuClaveSecretaAqui..."
   ```
6. **Seguridad Absoluta:** Esta variable de entorno nunca se compila ni se expone al cliente React/Vite.

---

## 3. Límites y Restricciones del Modelo (System Prompt)
Gemini opera bajo directrices deterministas estrictas:
- **Prohibición de Alucinación Numérica:** Gemini no puede inventar valores ni cambiar los datos recibidos del sensor.
- **Prohibición de Certificación:** No puede declarar que el agua es "100% potable" ni emitir diagnósticos médicos. Solo 3 parámetros físicos no sustituyen el análisis integral de laboratorio.
- **Respaldo Normativo:** Contextualiza según la Resolución 2115 de 2007 (pH entre 6.5 y 9.0; turbidez hasta 2 NTU).
- **Resiliencia:** Si la API de Gemini no responde o no hay clave configurada, el backend devuelve un mensaje explicativo y el Semáforo Virtual y las mediciones siguen funcionando al 100%.
