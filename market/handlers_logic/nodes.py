from typing import List

from sqlalchemy import Integer, cast, except_
from sqlalchemy.sql import func
from sqlalchemy.sql.functions import coalesce

from market.db.schema import ShopUnit
from market.db.sql_session import session
from market.utils import datetime_to_iso


def get_units_tuple_from_subtree(unit_id: str) -> List[tuple]:
    """
    Gets tuples of nodes from subtree with updated average price
    Tuples look like this: (unit_id, name, parent_id, type, price, date, level)
    """
    local_root_query = (
        session.query(ShopUnit)
        .filter(ShopUnit.unit_id == unit_id)
        .cte("cte", recursive=True)
    )
    bottom_subtree_query = session.query(ShopUnit).join(
        local_root_query, ShopUnit.parent_id == local_root_query.c.unit_id
    )
    subtree_query = local_root_query.union(bottom_subtree_query)

    leaves_query = (
        session.query(subtree_query)
        .with_entities(
            subtree_query.c.unit_id,
            subtree_query.c.price,
            subtree_query.c.parent_id,
        )
        .where(subtree_query.c.price != None)
        .cte("cte2", recursive=True)
    )

    top_sum_query = (
        session.query(leaves_query)
        .join(subtree_query, leaves_query.c.parent_id == subtree_query.c.unit_id)
        .with_entities(
            subtree_query.c.unit_id,
            coalesce(subtree_query.c.price, 0) + leaves_query.c.price,
            subtree_query.c.parent_id,
        )
    )
    sum_tree_query = leaves_query.union(top_sum_query)

    grouped_sum_query = (
        session.query(
            sum_tree_query.c.unit_id,
            cast(func.floor(func.avg(sum_tree_query.c.price)), Integer).label(
                "avg_price"
            ),
            sum_tree_query.c.parent_id,
        )
        .group_by(sum_tree_query.c.unit_id, sum_tree_query.c.parent_id)
        .cte("cte3", recursive=False)
    )

    categories_sum_query = (
        session.query(ShopUnit)
        .join(grouped_sum_query, grouped_sum_query.c.unit_id == ShopUnit.unit_id)
        .with_entities(
            ShopUnit.unit_id,
            ShopUnit.name,
            ShopUnit.parent_id,
            ShopUnit.type,
            grouped_sum_query.c.avg_price,
            ShopUnit.date,
            ShopUnit.level,
        )
        .cte("cte4", recursive=False)
    )

    empty_categories_query = except_(
        session.query(subtree_query).with_entities(
            subtree_query.c.unit_id.label("unit_id")
        ),
        session.query(categories_sum_query).with_entities(
            categories_sum_query.c.unit_id.label("unit_id")
        ),
    ).cte("cte5")

    units_tuples = (
        session.query(categories_sum_query).all()
        + session.query(empty_categories_query)
        .join(ShopUnit, empty_categories_query.c.unit_id == ShopUnit.unit_id)
        .with_entities(
            ShopUnit.unit_id,
            ShopUnit.name,
            ShopUnit.parent_id,
            ShopUnit.type,
            ShopUnit.price,
            ShopUnit.date,
            ShopUnit.level,
        )
        .all()
    )
    return units_tuples


def build_dict_from_units(units_tuples: List[tuple], unit_id: str) -> dict:
    """
    Builds nested dict from nodes
    """
    units_dicts = [
        {
            "id": u[0],
            "name": u[1],
            "parentId": u[2],
            "type": u[3],
            "price": u[4],
            "date": datetime_to_iso(u[5]),
            "children": [] if u[3] == "CATEGORY" else None,
            "level": u[6],
        }
        for u in units_tuples
    ]

    id2unit = {unit["id"]: unit for unit in units_dicts}

    level2units = {}
    for unit in units_dicts:
        if unit["level"] in level2units:
            level2units[unit["level"]].append(unit)
        else:
            level2units[unit["level"]] = [unit]
        unit.pop("level")

    for level in range(max(level2units.keys()), min(level2units.keys()), -1):
        for unit in level2units[level]:
            if not unit["parentId"] or unit["parentId"] not in id2unit.keys():
                continue
            parent = id2unit[unit["parentId"]]
            parent["date"] = max(parent["date"], unit["date"])

    for i, _ in enumerate(units_dicts):
        for j, _ in enumerate(units_dicts):
            if units_dicts[j]["parentId"] == units_dicts[i]["id"]:
                units_dicts[i]["children"].append(units_dicts[j])

    return [unit for unit in units_dicts if unit["id"] == unit_id][0]


def get_units_subtree(unit_id: str) -> dict:
    """
    Returns dict with nested structure of subtree if unit
    """
    units_tuples = get_units_tuple_from_subtree(unit_id)
    result = build_dict_from_units(units_tuples, unit_id)
    return result
