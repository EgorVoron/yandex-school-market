from typing import List

from market.db.schema import PriceUpdateLog, ShopUnit
from market.db.sql_session import session


def update_levels():
    """
    Unfinished function for levels updating
    """
    roots_query = (
        session.query(ShopUnit)
        .with_entities(
            ShopUnit.unit_id,
            ShopUnit.parent_id,
            ShopUnit.level,
        )
        .where(ShopUnit.parent_id == None)
        .cte("roots", recursive=True)
    )

    levels_sum_query = (
        session.query(ShopUnit)
        .join(roots_query, roots_query.c.unit_id == ShopUnit.parent_id)
        .with_entities(
            ShopUnit.unit_id,
            ShopUnit.parent_id,
            roots_query.c.level + 1,
        )
    )
    ...
