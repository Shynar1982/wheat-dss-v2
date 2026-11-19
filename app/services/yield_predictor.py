import datetime
from sqlalchemy import BigInteger, Date, Numeric, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import SessionLocal, Base

class SoilProperty(Base):
    __tablename__ = "soil_properties"
    field_id: Mapped[int] = mapped_column(BigInteger, primary_key=True) 
    ph: Mapped[float] = mapped_column(Numeric(5, 2))
    soc: Mapped[float] = mapped_column(Numeric(5, 2))
    no3: Mapped[float] = mapped_column(Numeric(6, 2))
    p205: Mapped[float] = mapped_column(Numeric(6, 2))
    k20: Mapped[float] = mapped_column(Numeric(6, 2))

class YieldPrediction(Base):
    __tablename__ = "yield_predictions"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    field_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("fields.field_id"))
    prediction_date: Mapped[datetime.date] = mapped_column(Date, server_default="now()")
    predicted_yield_t_ha: Mapped[float] = mapped_column(Numeric(6, 3))
    model_version: Mapped[str] = mapped_column(String(50))

async def train_and_predict(field_id: int):
    # Заглушка: возвращаем фиксированное значение 4.1 т/га
    async with SessionLocal() as session:
        new_pred = YieldPrediction(
            field_id=field_id,
            predicted_yield_t_ha=4.1,
            model_version="DummyModel"
        )
        session.add(new_pred)
        await session.commit()
        print(f"✅ Прогноз для поля {field_id}: 4.1 т/га (заглушка)")
        return 4.1
