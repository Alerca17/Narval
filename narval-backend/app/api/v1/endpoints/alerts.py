from typing import Optional
from fastapi import APIRouter, Depends, Query
from app.schemas.alert import AlertListResponse, AlertResponse
from app.repositories.alert_repository import AlertRepository
from app.api.deps import get_alert_repo

router = APIRouter()

@router.get(
    "",
    response_model=AlertListResponse,
    summary="Listado de alertas",
    description="Permite consultar alertas generadas por violaciones a los umbrales de referencia.",
)
def list_alerts(
    severity: Optional[str] = Query(None, description="Filtrar por INFO, WARNING, CRITICAL"),
    parameter_name: Optional[str] = Query(None, description="Filtrar por ph, turbidity, temperature"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    alert_repo: AlertRepository = Depends(get_alert_repo),
):
    items, total = alert_repo.list_alerts(
        severity=severity,
        parameter_name=parameter_name,
        limit=limit,
        offset=offset,
    )
    result_items = [
        AlertResponse(
            id=a.id,
            measurement_id=a.measurement_id,
            parameter_name=a.parameter_name,
            observed_value=a.observed_value,
            threshold_reference=a.threshold_reference,
            severity=a.severity,
            message=a.message,
            created_at=a.created_at,
        )
        for a in items
    ]
    return AlertListResponse(total=total, limit=limit, offset=offset, items=result_items)
