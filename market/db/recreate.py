from market.db.schema import ShopUnit
from market.db.sql_session import engine

ShopUnit.__table__.drop(engine)
ShopUnit.__table__.create(engine)
