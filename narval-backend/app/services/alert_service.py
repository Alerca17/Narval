from typing import List
from app.models.measurement import Measurement
from app.models.alert import Alert
from app.schemas.semaforo import VirtualSemaforoResponse, SemaforoColor
from app.repositories.alert_repository import AlertRepository

class AlertService:
    def __init__(self, alert_repo: AlertRepository):
        self.alert_repo = alert_repo

    def evaluate_and_generate_alerts(self, measurement: Measurement, semaforo: VirtualSemaforoResponse) -> List[Alert]:
        created_alerts = []

        # pH Alert
        if semaforo.ph.color in (SemaforoColor.YELLOW, SemaforoColor.RED):
            severity = "CRITICAL" if semaforo.ph.color == SemaforoColor.RED else "WARNING"
            alert = Alert(
                measurement_id=measurement.id,
                parameter_name="ph",
                observed_value=measurement.ph_value,
                threshold_reference="6.5 - 9.0 (Res. 2115 de 2007)",
                severity=severity,
                message=semaforo.ph.message,
            )
            created_alerts.append(self.alert_repo.create(alert))

        # Turbidity Alert
        if semaforo.turbidity.color in (SemaforoColor.YELLOW, SemaforoColor.RED):
            severity = "CRITICAL" if semaforo.turbidity.color == SemaforoColor.RED else "WARNING"
            alert = Alert(
                measurement_id=measurement.id,
                parameter_name="turbidity",
                observed_value=measurement.turbidity_value,
                threshold_reference="<= 2.0 NTU (Res. 2115 de 2007)",
                severity=severity,
                message=semaforo.turbidity.message,
            )
            created_alerts.append(self.alert_repo.create(alert))

        # Temperature Alert
        if semaforo.temperature.color in (SemaforoColor.YELLOW, SemaforoColor.RED):
            severity = "CRITICAL" if semaforo.temperature.color == SemaforoColor.RED else "WARNING"
            alert = Alert(
                measurement_id=measurement.id,
                parameter_name="temperature",
                observed_value=measurement.temperature_celsius,
                threshold_reference="10.0 - 30.0 °C",
                severity=severity,
                message=semaforo.temperature.message,
            )
            created_alerts.append(self.alert_repo.create(alert))

        return created_alerts
