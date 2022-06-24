from datetime import datetime
from typing import Union

from market.db.schema import ShopUnit
from market.db.sql_session import session


def unit_exists(unit_id: str) -> bool:
    return (
        session.query(ShopUnit).filter(ShopUnit.unit_id == unit_id).first() is not None
    )


def iso_to_datetime(dt_str: str) -> Union[bool, datetime]:
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except ValueError:
        return False
    return dt


def datetime_to_iso(dt: datetime) -> str:
    return dt.isoformat() + ".000Z"
