import sys

from tests.test_utils import deep_sort_children, print_diff, request


def test_scenario_atomicity():
    status, _ = request(
        "/imports",
        "POST",
        data={
            "updateDate": "2022-05-28T21:12:01.000Z",
            "items": [
                {
                    "id": "offer1",
                    "name": "a",
                    "type": "OFFER",
                    "parentId": None,
                    "price": 1,
                },
                {
                    "id": "offer2",
                    "name": "b",
                    "type": "OFFER",
                    "parentId": None,
                    "price": 1,
                },
                {"id": "offer3", "type": "OFFER", "parentId": None, "price": 1},
            ],
        },
    )
    assert status == 400, f"Expected HTTP status code 404, got {status}"
    status, result = request("/nodes/offer1", "GET")
    assert status == 404, f"Expected HTTP status code 404, got {status}"
    status, result = request("/nodes/offer2", "GET")
    assert status == 404, f"Expected HTTP status code 404, got {status}"
    status, result = request("/nodes/offer3", "GET")
    assert status == 404, f"Expected HTTP status code 404, got {status}"
    print("Test atomicity passed")


def test_scenario_parents_remove():
    status, _ = request(
        "/imports",
        "POST",
        data={
            "updateDate": "2022-05-28T21:12:01.000Z",
            "items": [
                {
                    "id": "root1",
                    "name": "a",
                    "type": "CATEGORY",
                    "parentId": None,
                    "price": None,
                },
                {
                    "id": "root2",
                    "name": "b",
                    "type": "CATEGORY",
                    "parentId": None,
                    "price": None,
                },
                {
                    "id": "subroot2.1",
                    "name": "c",
                    "type": "OFFER",
                    "parentId": "root2",
                    "price": 2,
                },
                {
                    "id": "subroot1.1",
                    "type": "OFFER",
                    "parentId": "root1",
                    "price": 1,
                    "name": "c",
                },
            ],
        },
    )

    assert status == 200, f"Expected HTTP status code 200, got {status}"

    status, _ = request("/delete/root1", "DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    status, _ = request("/delete/root2", "DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    status, _ = request("/nodes/root2", "GET")
    assert status == 404, f"Expected HTTP status code 404, got {status}"

    print("Test parents remove passed")


def test_twice_put_delete():
    status, _ = request(
        "/imports",
        "POST",
        data={
            "updateDate": "2022-05-28T21:12:00.000Z",
            "items": [
                {
                    "id": "root1",
                    "name": "a",
                    "type": "CATEGORY",
                    "parentId": None,
                    "price": None,
                },
            ],
        },
    )
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    status, _ = request(
        "/imports",
        "POST",
        data={
            "updateDate": "2022-05-28T21:12:01.000Z",
            "items": [
                {
                    "id": "root2",
                    "name": "root2",
                    "type": "CATEGORY",
                    "parentId": None,
                    "price": None,
                },
                {
                    "id": "subroot2.1",
                    "name": "subroot2.1",
                    "type": "CATEGORY",
                    "parentId": "root2",
                    "price": None,
                },
                {
                    "id": "subroot2.2",
                    "name": "subroot2.2",
                    "type": "OFFER",
                    "parentId": "root2",
                    "price": 3,
                },
                {
                    "id": "subroot2.3",
                    "name": "subroot2.3",
                    "type": "CATEGORY",
                    "parentId": "root2",
                    "price": None,
                },
                {
                    "id": "subroot2.4",
                    "name": "subroot2.4",
                    "type": "OFFER",
                    "parentId": "root2",
                    "price": 2,
                },
                {
                    "id": "subroot1.1",
                    "type": "OFFER",
                    "parentId": "root1",
                    "price": 1,
                    "name": "subroot1.1",
                },
            ],
        },
    )

    assert status == 200, f"Expected HTTP status code 200, got {status}"

    status, _ = request(
        "/imports",
        "POST",
        data={
            "updateDate": "2022-05-28T22:12:01.000Z",
            "items": [
                {
                    "id": "subroot2.1.1",
                    "name": "subroot2.1.1",
                    "type": "OFFER",
                    "parentId": "subroot2.1",
                    "price": 3,
                },
            ],
        },
    )

    status, tree = request("/nodes/root2", "GET", json_response=True)

    expected_tree = {
        "type": "CATEGORY",
        "name": "root2",
        "id": "root2",
        "price": 2,
        "parentId": None,
        "date": "2022-05-28T22:12:01.000Z",
        "children": [
            {
                "type": "OFFER",
                "name": "subroot2.4",
                "id": "subroot2.4",
                "price": 2,
                "parentId": "root2",
                "date": "2022-05-28T21:12:01.000Z",
                "children": None,
            },
            {
                "id": "subroot2.1",
                "name": "subroot2.1",
                "type": "CATEGORY",
                "parentId": "root2",
                "price": 3,
                "date": "2022-05-28T22:12:01.000Z",
                "children": [
                    {
                        "id": "subroot2.1.1",
                        "name": "subroot2.1.1",
                        "type": "OFFER",
                        "parentId": "subroot2.1",
                        "price": 3,
                        "date": "2022-05-28T22:12:01.000Z",
                        "children": None,
                    }
                ],
            },
            {
                "id": "subroot2.2",
                "name": "subroot2.2",
                "type": "OFFER",
                "parentId": "root2",
                "price": 3,
                "date": "2022-05-28T21:12:01.000Z",
                "children": None,
            },
            {
                "id": "subroot2.3",
                "name": "subroot2.3",
                "type": "CATEGORY",
                "parentId": "root2",
                "price": None,
                "children": [],
                "date": "2022-05-28T21:12:01.000Z",
            },
        ],
    }
    deep_sort_children(tree)
    deep_sort_children(expected_tree)
    if tree != expected_tree:
        print_diff(expected_tree, tree)
        print("Response tree doesn't match expected tree.")
        sys.exit(1)

    status, _ = request("/delete/subroot2.1", "DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    status, tree = request("/nodes/root2", "GET", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    expected_tree = {
        "type": "CATEGORY",
        "name": "root2",
        "id": "root2",
        "price": 2,
        "parentId": None,
        "date": "2022-05-28T22:12:01.000Z",
        "children": [
            {
                "type": "OFFER",
                "name": "subroot2.4",
                "id": "subroot2.4",
                "price": 2,
                "parentId": "root2",
                "date": "2022-05-28T21:12:01.000Z",
                "children": None,
            },
            {
                "id": "subroot2.2",
                "name": "subroot2.2",
                "type": "OFFER",
                "parentId": "root2",
                "price": 3,
                "date": "2022-05-28T21:12:01.000Z",
                "children": None,
            },
            {
                "id": "subroot2.3",
                "name": "subroot2.3",
                "type": "CATEGORY",
                "parentId": "root2",
                "price": None,
                "children": [],
                "date": "2022-05-28T21:12:01.000Z",
            },
        ],
    }

    deep_sort_children(tree)
    deep_sort_children(expected_tree)
    if tree != expected_tree:
        print_diff(expected_tree, tree)
        print("Response tree doesn't match expected tree 2.")
        sys.exit(1)

    status, _ = request("/delete/root2", "DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    status, tree = request("/delete/root1", "DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    print("Test twice put delete passed.")


def test_time_segments():
    def get_item_data(id: str, day: int, hour: int):
        return {
            "updateDate": f"2022-01-0{day}T0{hour}:00:00.000Z",
            "items": [
                {
                    "id": id,
                    "name": id,
                    "type": "OFFER",
                    "parentId": None,
                    "price": 1,
                }
            ],
        }

    status, _ = request("/imports", "POST", data=get_item_data("1", 2, 0))
    status, _ = request("/imports", "POST", data=get_item_data("1", 2, 1))
    status, _ = request("/imports", "POST", data=get_item_data("2", 2, 1))
    status, _ = request("/imports", "POST", data=get_item_data("2", 2, 2))
    status, _ = request("/imports", "POST", data=get_item_data("3", 1, 3))
    status, _ = request("/imports", "POST", data=get_item_data("3", 1, 4))
    status, _ = request("/imports", "POST", data=get_item_data("4", 2, 5))

    status, updated_items = request(
        "/sales?date=2022-01-03T00:00:00.000Z", "GET", json_response=True
    )

    expected_items = [
        {
            "date": "2022-01-02T01:00:00.000Z",
            "id": "1",
            "name": "1",
            "parentId": None,
            "price": 1,
            "type": "OFFER",
        },
        {
            "date": "2022-01-02T02:00:00.000Z",
            "id": "2",
            "name": "2",
            "parentId": None,
            "price": 1,
            "type": "OFFER",
        },
        {
            "date": "2022-01-02T05:00:00.000Z",
            "id": "4",
            "name": "4",
            "parentId": None,
            "price": 1,
            "type": "OFFER",
        },
    ]
    print(updated_items)
    assert sorted(expected_items, key=lambda x: x.items()) == sorted(
        updated_items, key=lambda x: x.items()
    )

    request("/delete/1", "DELETE")

    status, updated_items = request(
        "/sales?date=2022-01-03T00:00:00.000Z", "GET", json_response=True
    )

    expected_items = [
        {
            "date": "2022-01-02T02:00:00.000Z",
            "id": "2",
            "name": "2",
            "parentId": None,
            "price": 1,
            "type": "OFFER",
        },
        {
            "date": "2022-01-02T05:00:00.000Z",
            "id": "4",
            "name": "4",
            "parentId": None,
            "price": 1,
            "type": "OFFER",
        },
    ]

    assert sorted(expected_items, key=lambda x: x.items()) == sorted(
        updated_items, key=lambda x: x.items()
    )

    request("/delete/2", "DELETE")
    request("/delete/3", "DELETE")
    request("/delete/4", "DELETE")

    print("Test time segments passed")


def test_all():
    test_scenario_atomicity()
    test_scenario_parents_remove()
    test_twice_put_delete()
    test_time_segments()


if __name__ == "__main__":
    test_all()
