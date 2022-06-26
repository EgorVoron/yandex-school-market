from datetime import datetime, timedelta
from typing import List

from market.db.schema import PriceUpdateLog, ShopUnit
from market.db.sql_session import session
from market.utils import datetime_to_iso


def get_price_updated_units_tuples(date_to: datetime) -> List[tuple]:
    """
    Returns tuples of units (offers), updated between date_from and date_to
    Tuples look like this: (unit_id, name, parent_id, type, price, date)
    """
    date_from = date_to - timedelta(hours=24)
    return (
        session.query(PriceUpdateLog)
        .where(PriceUpdateLog.date.between(date_from, date_to))
        .join(ShopUnit, PriceUpdateLog.unit_id == ShopUnit.unit_id)
        .with_entities(
            PriceUpdateLog.unit_id,
            ShopUnit.name,
            ShopUnit.parent_id,
            ShopUnit.type,
            ShopUnit.price,
            ShopUnit.date,
        )
        .distinct()
        .all()
    )


def get_price_updated_units(date_to: datetime) -> List[dict]:
    """
    Returns formatted dicts with updated units
    """
    units_tuples = get_price_updated_units_tuples(date_to)
    updated_units_dicts = []
    for unit_tuple in units_tuples:
        unit = {
            "id": unit_tuple[0],
            "name": unit_tuple[1],
            "parentId": unit_tuple[2],
            "type": unit_tuple[3],
            "price": unit_tuple[4],
            "date": datetime_to_iso(unit_tuple[5]),
        }
        updated_units_dicts.append(unit)
    return updated_units_dicts
