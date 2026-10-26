from enum import Enum
from typing import Optional
from pydantic import BaseModel

class SemaforoColor(str, Enum):
    GREEN = "GREEN"      # Óptimo según Resolución 2115/2007
    YELLOW = "YELLOW"    # Advertencia / Fuera de rango óptimo moderado
    RED = "RED"          # Crítico / Fuera de rango severo
    GRAY = "GRAY"        # Sin calibrar / Desconectado / Sin datos

class ParameterEvaluation(BaseModel):
    parameter: str  # pH, turbidez, temperatura
    color: SemaforoColor
    value: Optional[float] = None
    voltage: Optional[float] = None
    unit: str
    status_label: str  # "Óptimo", "Alerta", "Crítico", "Calibración Pendiente", "Error"
    message: str
    is_calibrated: bool

class VirtualSemaforoResponse(BaseModel):
    global_status: SemaforoColor
    global_label: str
    global_summary: str
    ph: ParameterEvaluation
    turbidity: ParameterEvaluation
    temperature: ParameterEvaluation
    notes: Optional[str] = None
