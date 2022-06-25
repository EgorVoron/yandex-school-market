from typing import List

from market.db.schema import PriceUpdateLog, ShopUnit
from market.db.sql_session import session
from market.handlers_logic.nodes import get_units_subtree


def get_update_time(unit_id: str):
    """
    Counts last update time of node. Will be used to update 'date' field of parent of deleted node
    """
    return get_units_subtree(unit_id)["date"]


def get_subtree(unit_id: str) -> List[str]:
    """
    Returns indices of nodes to remove
    """
    local_root_query = (
        session.query(ShopUnit)
        .filter(ShopUnit.unit_id == unit_id)
        .cte("cte", recursive=True)
    )
    bottom_subtree_query = session.query(ShopUnit).join(
        local_root_query, ShopUnit.parent_id == local_root_query.c.unit_id
    )
    dfs_query = local_root_query.union(bottom_subtree_query)
    subtree_indices = [
        obj[0]
        for obj in session.query(dfs_query).with_entities(dfs_query.c.unit_id).all()
    ]
    return subtree_indices


def remove_unit(unit_id: str) -> None:
    """
    Deletes subtree, updates 'date' of deleted node's parent and deletes price updates logs of nodes from subtree
    """
    subtree_indices = get_subtree(unit_id)

    unit = session.query(ShopUnit).where(ShopUnit.unit_id == unit_id).first()
    parent_id = unit.parent_id

    session.query(ShopUnit).where(ShopUnit.unit_id == parent_id).update(
        {
            ShopUnit.date: get_update_time(unit_id),
        }
    )
    session.commit()

    session.query(ShopUnit).where(ShopUnit.unit_id.in_(subtree_indices)).delete()
    session.query(PriceUpdateLog).where(
        PriceUpdateLog.unit_id.in_(subtree_indices)
    ).delete()
    session.commit()
