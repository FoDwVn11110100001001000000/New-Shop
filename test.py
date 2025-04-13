from database.models import Lots, Products
from database.models import session
from sqlalchemy import func

results = (
    session.query(
        Lots.lot_type,
        Products.price,
        func.count(Lots.id).label('count')
    )
    .join(Products, Products.lot_type == Lots.lot_type)
    .group_by(Lots.lot_type, Products.price)
    .all()
)

for lot_type, price, count in results:
    print(f"Тип: {lot_type}, Цена: {price}, Количество: {count}")