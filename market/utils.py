from datetime import datetime
from typing import Union

from market.db.schema import ShopUnit
from market.db.sql_session import session


def unit_exists(unit_id: str) -> bool:
    return (
        session.query(ShopUnit).filter(ShopUnit.unit_id == unit_id).first() is not None
    )


def iso_to_datetime(dt_str: str) -> Union[bool, datetime]:
    if not dt_str:
        return False
    if "T" not in dt_str or "Z" not in dt_str:
        return False  # 'datetime' module doesn't check if T/Z are in string, but raises error if they're wrongly placed
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except ValueError:
        return False
    return dt
# upd

def datetime_to_iso(dt: datetime) -> str:
    return dt.isoformat() + ".000Z"
