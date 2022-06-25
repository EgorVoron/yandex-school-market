from datetime import datetime
from typing import Any, Callable, Dict, List

from market.db.schema import PriceUpdateLog, ShopUnit
from market.db.sql_session import session

required_fields = ["id", "name", "type"]
type_values = ["CATEGORY", "OFFER"]

item_t = Dict[str, Any]


def check_fields(item: item_t) -> bool:
    for field in required_fields:
        if not item.get(field):
            return False
    return item["type"] in type_values


def check_name(item: item_t) -> bool:
    return item["name"] is not None


def check_price(item: item_t) -> bool:
    if "price" not in item.keys():
        return True
    if item["type"] == "CATEGORY":
        return item["price"] is None
    if item["type"] == "OFFER":
        return isinstance(item["price"], int) and item["price"] >= 0


def check_parent(item: item_t) -> bool:
    if not item.get("parentId"):
        return True
    parent_unit = (
        session.query(ShopUnit).filter(ShopUnit.unit_id == item["parentId"]).first()
    )
    if not parent_unit:
        return False
    return parent_unit.type == "CATEGORY"


checkers: List[Callable] = [check_fields, check_name, check_price, check_parent]


def validate_shop_unit(item: item_t) -> bool:
    for checker in checkers:
        if not checker(item):
            return False
    return True


def count_level(item: item_t) -> int:
    parent_id = item.get("parentId")
    level = 0
    if parent_id:
        parent_unit = (
            session.query(ShopUnit).filter(ShopUnit.unit_id == parent_id).one()
        )
        level = parent_unit.level + 1
    return level


def update_shop_unit(item: item_t, update_date: datetime) -> None:
    session.query(ShopUnit).filter(ShopUnit.unit_id == item["id"]).update(
        {
            ShopUnit.name: item["name"],
            ShopUnit.parent_id: item.get("parentId"),
            ShopUnit.type: item["type"],
            ShopUnit.price: item.get("price"),
            ShopUnit.date: update_date,
        }
    )
    if "price" not in item.keys():
        return
    price_update_log = PriceUpdateLog(unit_id=item["id"], date=update_date)
    session.add(price_update_log)


def create_shop_unit(item: item_t, update_date: datetime) -> None:
    level = count_level(item)

    shop_unit = ShopUnit(
        unit_id=item["id"],
        name=item["name"],
        parent_id=item.get("parentId"),
        type=item["type"],
        price=item.get("price"),
        date=update_date,
        level=level,
    )
    session.add(shop_unit)


def post_shop_unit(item: item_t, update_date: datetime) -> bool:
    if not validate_shop_unit(item):
        return False

    inserted_unit = (
        session.query(ShopUnit).filter(ShopUnit.unit_id == item["id"]).first()
    )
    if inserted_unit:
        if inserted_unit.type != item["type"]:
            return False
        update_shop_unit(item, update_date)
    else:
        create_shop_unit(item, update_date)

    return True


def validate_items_id_list(items: List[item_t]) -> bool:
    if not items:
        return False
    id_list = [item["id"] for item in items]
    return len(set(id_list)) == len(id_list)


def post_shop_units(items: List[item_t], update_date: datetime) -> bool:
    if not validate_items_id_list(items):
        return False
    for item in items:
        result: bool = post_shop_unit(item, update_date)
        if not result:
            session.rollback()
            return False
    session.commit()
    return True
