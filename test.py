from sqlalchemy import func
from database.models import Account, session

results = (
    session.query(
        Account.lot_type,
        Account.price,
        func.count(Account.id).label("quantity")
    )
    .group_by(Account.lot_type, Account.price)
    .order_by(Account.lot_type)
    .all()
)

for lot_type, price, quantity in results:
    print(f"Тип лота: {lot_type} /// Цена: {price} /// Кол-во: {quantity}")
