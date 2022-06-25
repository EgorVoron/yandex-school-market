from typing import Any, Dict, List

from flask import jsonify, request

from market.handlers_logic import (get_price_updated_units, get_units_subtree,
                                   post_shop_units, remove_unit)
from market.utils import iso_to_datetime, unit_exists

validation_failed_response = {"code": 400, "message": "Validation Failed"}, 400
ok_response = {"result": "ok"}, 200
not_found_response = {"code": 404, "message": "Item not found"}, 404


def imports():
    items: List[Dict[str, Any]] = request.json.get("items")
    update_date = iso_to_datetime(request.json.get("updateDate"))
    if not update_date:
        return validation_failed_response
    result: bool = post_shop_units(items, update_date)
    return ok_response if result else validation_failed_response


def delete(id):
    if not unit_exists(id):
        return not_found_response
    remove_unit(id)
    return ok_response


def nodes(id):
    if not unit_exists(id):
        return not_found_response
    result: dict = get_units_subtree(id)
    return jsonify(result), 200


def sales():
    date_to = iso_to_datetime(request.args.get("date"))
    if not date_to:
        return validation_failed_response
    result: List[dict] = get_price_updated_units(date_to)
    return jsonify(result), 200
