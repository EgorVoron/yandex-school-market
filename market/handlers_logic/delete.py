from typing import List

from market.db.schema import ShopUnit
from market.db.sql_session import session


def get_subtree(unit_id: str) -> List[str]:
    local_root_cte = (
        session.query(ShopUnit)
        .with_entities(ShopUnit.unit_id, ShopUnit.parent_id)
        .filter(ShopUnit.unit_id == unit_id)
        .cte("cte", recursive=True)
    )

    bottom_query = (
        session.query(ShopUnit)
        .with_entities(ShopUnit.unit_id, ShopUnit.parent_id)
        .join(local_root_cte, ShopUnit.parent_id == local_root_cte.c.unit_id)
    )

    dfs_query = local_root_cte.union(bottom_query)
    subtree_indices = [
        obj[0] for obj in session.query(dfs_query).with_entities(ShopUnit.unit_id)
    ]
    return subtree_indices


def remove_unit(unit_id: str) -> None:
    subtree_indices = get_subtree(unit_id)
    session.query(ShopUnit).where(ShopUnit.unit_id.in_(subtree_indices)).delete()
    session.commit()
