from datetime import datetime
from typing import Any, Callable, Dict, List

from market.db.schema import PriceUpdateLog, ShopUnit
from market.db.sql_session import session

required_fields = ["id", "name", "type"]
type_values = ["CATEGORY", "OFFER"]

item_t = Dict[str, Any]


def check_item_fields(item: item_t) -> bool:
    """
    Checks required fields presence and format
    """
    for field in required_fields:
        if not item.get(field):
            return False
    return item["type"] in type_values


def check_item_price(item: item_t) -> bool:
    """
    Checks if price value is correct
    """
    if item["type"] == "CATEGORY":
        return item.get("price") is None
    if item["type"] == "OFFER":
        return "price" in item.keys() and isinstance(item["price"], int) and item["price"] >= 0


item_checkers: List[Callable] = [check_item_fields, check_item_price]


def validate_item(item: item_t) -> bool:
    """
    Validates item's fields
    """
    for checker in item_checkers:
        if not checker(item):
            return False
    return True


def check_items_id_list(id_list: List[str]) -> bool:
    """
    Checks if there are items with the same id
    """
    return len(set(id_list)) == len(id_list)


def check_items_parents(items: List[item_t], id2item: Dict[str, dict]) -> bool:
    """
    Checks if item's parent's type is CATEGORY
    :param items: list of all items
    :param id2item: {id: item}
    """
    for item in items:
        if not item.get("parentId"):
            continue
        if item["parentId"] in id2item.keys():
            return id2item[item["parentId"]]["type"] == "CATEGORY"

        parent_unit = (
            session.query(ShopUnit).filter(ShopUnit.unit_id == item["parentId"]).first()
        )
        if not parent_unit:
            return False
        if parent_unit.type != "CATEGORY":
            return False
    return True


def validate_items(items: List[item_t]) -> bool:
    """
    Checks if there are incorrect items in input
    """
    if not items:
        return False
    for item in items:
        if not validate_item(item):
            return False
    id2item: Dict[str, dict] = {item["id"]: item for item in items}
    id_list = [item["id"] for item in items]
    if not check_items_id_list(id_list):
        return False
    if not check_items_parents(items, id2item):
        return False
    return True


def count_level(item: item_t) -> int:
    """
    Counts level of the new node. If I had more time, I would implement something like "update_levels" from levels.py,
    since there can be a situation, where node's level is changed because of it's ancestors changes. Current
    implementation is naive and supposes that node's levels stay constant.
    """
    parent_id = item.get("parentId")
    level = 0
    if parent_id:
        parent_unit = (
            session.query(ShopUnit).filter(ShopUnit.unit_id == parent_id).one()
        )
        level = parent_unit.level + 1
    return level


def update_shop_unit(item: item_t, update_date: datetime) -> None:
    """
    Updates unit's fields in DB, if unit already exists
    """
    session.query(ShopUnit).filter(ShopUnit.unit_id == item["id"]).update(
        {
            ShopUnit.name: item["name"],
            ShopUnit.parent_id: item.get("parentId"),
            ShopUnit.type: item["type"],
            ShopUnit.price: item.get("price"),
            ShopUnit.date: update_date,
            ShopUnit.level: count_level(item),
        }
    )


def create_shop_unit(item: item_t, update_date: datetime) -> None:
    """
    Creates unit from item's fields
    """
    shop_unit = ShopUnit(
        unit_id=item["id"],
        name=item["name"],
        parent_id=item.get("parentId"),
        type=item["type"],
        price=item.get("price"),
        date=update_date,
        level=count_level(item),
    )
    session.add(shop_unit)


def post_shop_unit(item: item_t, update_date: datetime) -> bool:
    inserted_unit = (
        session.query(ShopUnit).filter(ShopUnit.unit_id == item["id"]).first()
    )
    if inserted_unit:
        if inserted_unit.type != item["type"]:
            return False
        update_shop_unit(item, update_date)
    else:
        create_shop_unit(item, update_date)
    if item["type"] == "OFFER":
        # add info about offer's price update to db
        price_update_log = PriceUpdateLog(unit_id=item["id"], date=update_date)
        session.add(price_update_log)
    return True


def post_shop_units(items: List[item_t], update_date: datetime) -> bool:
    """
    Posts (creates or updates) all units and returns True, if they're correct,
    in other case returns False
    """
    if not validate_items(items):
        return False
    for item in items:
        result: bool = post_shop_unit(item, update_date)
        if not result:
            session.rollback()
            return False
    session.commit()
    return True
