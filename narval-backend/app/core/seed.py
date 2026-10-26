from app.core.database import SessionLocal
from app.models.reference_rule import ReferenceRule

def seed():
    db = SessionLocal()
    try:
        rules = [
            ReferenceRule(
                parameter_name="ph",
                source="Resolución 2115 de 2007 (Art. 2)",
                min_value=6.5,
                max_value=9.0,
                unit="pH",
                is_active=True,
                version="1.0"
            ),
            ReferenceRule(
                parameter_name="turbidity",
                source="Resolución 2115 de 2007 (Art. 2)",
                min_value=0.0,
                max_value=2.0,
                unit="NTU",
                is_active=True,
                version="1.0"
            ),
            ReferenceRule(
                parameter_name="temperature",
                source="Rango ambiental aceptable para acueductos rurales",
                min_value=10.0,
                max_value=30.0,
                unit="°C",
                is_active=True,
                version="1.0"
            ),
        ]
        
        for rule in rules:
            existing = db.query(ReferenceRule).filter(
                ReferenceRule.parameter_name == rule.parameter_name,
                ReferenceRule.version == rule.version
            ).first()
            if not existing:
                db.add(rule)
        
        db.commit()
        print("Reglas de referencia normativas sembradas exitosamente.")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
