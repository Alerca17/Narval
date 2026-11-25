import pytest
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


@pytest.mark.parametrize(
    "value,expected_color",
    [
        (5.99, SemaforoColor.RED),
        (6.00, SemaforoColor.YELLOW),
        (6.49, SemaforoColor.YELLOW),
        (6.50, SemaforoColor.GREEN),
        (9.00, SemaforoColor.GREEN),
        (9.01, SemaforoColor.YELLOW),
        (9.50, SemaforoColor.YELLOW),
        (9.51, SemaforoColor.RED),
    ],
)
def test_ph_exact_boundaries_res_2115(value, expected_color):
    """CP-M4-01: Valores frontera exactos de pH según la Resolución 2115 de 2007."""
    res = VirtualSemaforoEngine.evaluate_ph(value=value, voltage=2.0, is_calibrated=True)
    assert res.color == expected_color


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


@pytest.mark.parametrize(
    "value,expected_color",
    [
        (0.0, SemaforoColor.GREEN),
        (2.0, SemaforoColor.GREEN),
        (2.01, SemaforoColor.YELLOW),
        (5.0, SemaforoColor.YELLOW),
        (5.01, SemaforoColor.RED),
    ],
)
def test_turbidity_exact_boundaries_res_2115(value, expected_color):
    """CP-M4-02: Valores frontera exactos de turbidez en NTU."""
    res = VirtualSemaforoEngine.evaluate_turbidity(value=value, voltage=2.5, is_calibrated=True)
    assert res.color == expected_color


def test_temperature_evaluation():
    res = VirtualSemaforoEngine.evaluate_temperature(21.5)
    assert res.color == SemaforoColor.GREEN
    res_warn = VirtualSemaforoEngine.evaluate_temperature(33.0)
    assert res_warn.color == SemaforoColor.YELLOW
    res_crit = VirtualSemaforoEngine.evaluate_temperature(45.0)
    assert res_crit.color == SemaforoColor.RED
    res_err = VirtualSemaforoEngine.evaluate_temperature(None)
    assert res_err.color == SemaforoColor.GRAY
    assert res_err.status_label == "Error Sensor"


@pytest.mark.parametrize(
    "celsius,expected_color",
    [
        (4.9, SemaforoColor.RED),
        (5.0, SemaforoColor.YELLOW),
        (9.9, SemaforoColor.YELLOW),
        (10.0, SemaforoColor.GREEN),
        (30.0, SemaforoColor.GREEN),
        (30.1, SemaforoColor.YELLOW),
        (38.0, SemaforoColor.YELLOW),
        (38.1, SemaforoColor.RED),
        (None, SemaforoColor.GRAY),
    ],
)
def test_temperature_exact_boundaries(celsius, expected_color):
    """CP-M4-03: Valores frontera exactos de temperatura y manejo de None."""
    res = VirtualSemaforoEngine.evaluate_temperature(celsius)
    assert res.color == expected_color


def test_evaluate_measurement_global_precedence():
    """CP-M4-04: Reglas de precedencia global (None->GRAY, RED > YELLOW > GRAY parcial > GREEN)."""
    # A) Sin medición registrada
    empty = VirtualSemaforoEngine.evaluate_measurement(None)
    assert empty.global_status == SemaforoColor.GRAY
    assert empty.global_label == "Sin Mediciones"

    # B) Todos los parámetros óptimos (GREEN)
    m_green = Measurement(
        device_id=1, packet_id="g1", ph_value=7.0, turbidity_value=1.0,
        temperature_celsius=20.0, calibration_status="CALIBRATED", quality_status="VALID",
    )
    res_green = VirtualSemaforoEngine.evaluate_measurement(m_green)
    assert res_green.global_status == SemaforoColor.GREEN

    # C) RED prevalece sobre GREEN
    m_red = Measurement(
        device_id=1, packet_id="r1", ph_value=5.1, turbidity_value=1.0,
        temperature_celsius=20.0, calibration_status="CALIBRATED", quality_status="VALID",
    )
    res_red = VirtualSemaforoEngine.evaluate_measurement(m_red)
    assert res_red.global_status == SemaforoColor.RED

    # D) Calibración mixta (pH calibrado GREEN, turbidez sin calibrar GRAY) -> global YELLOW
    m_partial = Measurement(
        device_id=1, packet_id="p1", ph_value=7.2, ph_voltage=2.0,
        turbidity_value=None, turbidity_voltage=2.5,
        temperature_celsius=20.0, calibration_status="PENDING", quality_status="PARTIAL",
    )
    res_partial = VirtualSemaforoEngine.evaluate_measurement(m_partial)
    assert res_partial.ph.color == SemaforoColor.GREEN
    assert res_partial.turbidity.color == SemaforoColor.GRAY
    assert res_partial.global_status == SemaforoColor.YELLOW
    assert res_partial.global_label == "Datos Parciales / Calibración Pendiente"
    assert "Turbidez" in (res_partial.notes or "")

    # E) YELLOW + GRAY -> Estado de Alerta
    m_warn = Measurement(
        device_id=1, packet_id="w1", ph_value=6.2, turbidity_value=1.0,
        temperature_celsius=None, calibration_status="CALIBRATED", quality_status="PARTIAL",
    )
    res_warn = VirtualSemaforoEngine.evaluate_measurement(m_warn)
    assert res_warn.global_status == SemaforoColor.YELLOW
    assert res_warn.global_label == "Estado de Alerta"
