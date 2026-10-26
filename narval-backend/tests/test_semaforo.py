from app.services.semaforo_service import VirtualSemaforoEngine
from app.schemas.semaforo import SemaforoColor
from app.models.measurement import Measurement

def test_ph_evaluation_optimal():
    res = VirtualSemaforoEngine.evaluate_ph(value=7.2, voltage=2.0, is_calibrated=True)
    assert res.color == SemaforoColor.GREEN
    assert res.status_label == "Óptimo"

def test_ph_evaluation_alert():
    res = VirtualSemaforoEngine.evaluate_ph(value=6.3, voltage=2.2, is_calibrated=True)
    assert res.color == SemaforoColor.YELLOW
    assert res.status_label == "Alerta"

def test_ph_evaluation_critical():
    res = VirtualSemaforoEngine.evaluate_ph(value=5.4, voltage=2.6, is_calibrated=True)
    assert res.color == SemaforoColor.RED
    assert res.status_label == "Crítico"

def test_ph_evaluation_uncalibrated():
    res = VirtualSemaforoEngine.evaluate_ph(value=7.0, voltage=2.0, is_calibrated=False)
    assert res.color == SemaforoColor.GRAY
    assert res.status_label == "Calibración Pendiente"

def test_turbidity_optimal():
    res = VirtualSemaforoEngine.evaluate_turbidity(value=1.5, voltage=3.8, is_calibrated=True)
    assert res.color == SemaforoColor.GREEN
    assert res.status_label == "Óptimo"

def test_turbidity_alert():
    res = VirtualSemaforoEngine.evaluate_turbidity(value=3.2, voltage=2.9, is_calibrated=True)
    assert res.color == SemaforoColor.YELLOW
    assert res.status_label == "Alerta"

def test_turbidity_critical():
    res = VirtualSemaforoEngine.evaluate_turbidity(value=8.0, voltage=1.5, is_calibrated=True)
    assert res.color == SemaforoColor.RED
    assert res.status_label == "Crítico"

def test_turbidity_uncalibrated():
    res = VirtualSemaforoEngine.evaluate_turbidity(value=None, voltage=3.5, is_calibrated=False)
    assert res.color == SemaforoColor.GRAY
    assert res.status_label == "Calibración Pendiente"

def test_temperature_evaluation():
    # Normal
    res = VirtualSemaforoEngine.evaluate_temperature(21.5)
    assert res.color == SemaforoColor.GREEN
    # Anormal / Advertencia
    res_warn = VirtualSemaforoEngine.evaluate_temperature(33.0)
    assert res_warn.color == SemaforoColor.YELLOW
    # Extremo / Crítico
    res_crit = VirtualSemaforoEngine.evaluate_temperature(45.0)
    assert res_crit.color == SemaforoColor.RED
    # Fallo OneWire
    res_err = VirtualSemaforoEngine.evaluate_temperature(None)
    assert res_err.color == SemaforoColor.GRAY
    assert res_err.status_label == "Error Sensor"
