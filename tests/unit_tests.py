import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from tests.test_utils import (API_BASEURL, deep_sort_children, print_diff,
                              request)


def test_check_fields():
    status, _ = request(
        "/imports",
        method="POST",
        data={
            "updateDate": "2022-02-03T15:00:00.000Z",
            "items": [{"type": "OFFER", "id": "b"}],
        },
    )
    assert status == 400


def test_check_name():
    status, _ = request(
        "/imports",
        method="POST",
        data={
            "updateDate": "2022-02-03T15:00:00.000Z",
            "items": [{"type": "OFFER", "id": "b", "name": None}],
        },
    )
    assert status == 400


def test_check_price_1():
    status, _ = request(
        "/imports",
        method="POST",
        data={
            "updateDate": "2022-02-03T15:00:00.000Z",
            "items": [{"type": "OFFER", "id": "b", "name": "a", "price": None}],
        },
    )
    assert status == 400


def test_check_price_2():
    status, _ = request(
        "/imports",
        method="POST",
        data={
            "updateDate": "2022-02-03T15:00:00.000Z",
            "items": [{"type": "OFFER", "id": "b", "name": "a", "price": -2}],
        },
    )
    assert status == 400


def test_check_price_3():
    status, _ = request(
        "/imports",
        method="POST",
        data={
            "updateDate": "2022-02-03T15:00:00.000Z",
            "items": [{"type": "CATEGORY", "id": "b", "name": "a", "price": 3}],
        },
    )
    assert status == 400


def test_check_time():
    status, _ = request(
        "/imports",
        method="POST",
        data={
            "updateDate": "2022-02-03 15:00:00.000",
            "items": [{"type": "CATEGORY", "id": "b", "name": "a", "price": None}],
        },
    )
    assert status == 400


def test_check_id():
    status, _ = request(
        "/imports",
        method="POST",
        data={
            "updateDate": "2022-02-03T15:00:00.000Z",
            "items": [
                {"type": "CATEGORY", "id": "b", "name": "a", "price": None},
                {"type": "CATEGORY", "id": "b", "name": "a", "price": None},
            ],
        },
    )
    assert status == 400


def test_post():
    for index, batch in enumerate(IMPORT_BATCHES):
        status, _ = request("/imports", method="POST", data=batch)

        assert status == 200, f"Expected HTTP status code 200, got {status}"


def test_imports():
    test_check_fields()
    test_check_name()
    test_check_price_1()
    test_check_price_2()
    test_check_price_3()
    test_check_time()
    test_check_id()
    print("Test imports checks & validations passed.")
    test_post()
    print("Test imports passed.")


ROOT_ID = "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1"

IMPORT_BATCHES = [
    {
        "items": [
            {
                "type": "CATEGORY",
                "name": "Товары",
                "id": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
                "parentId": None,
            }
        ],
        "updateDate": "2022-02-01T12:00:00.000Z",
    },
    {
        "items": [
            {
                "type": "CATEGORY",
                "name": "Смартфоны",
                "id": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
                "parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
            },
            {
                "type": "OFFER",
                "name": "jPhone 13",
                "id": "863e1a7a-1304-42ae-943b-179184c077e3",
                "parentId": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
                "price": 79999,
            },
            {
                "type": "OFFER",
                "name": "Xomiа Readme 10",
                "id": "b1d8fd7d-2ae3-47d5-b2f9-0f094af800d4",
                "parentId": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
                "price": 59999,
            },
        ],
        "updateDate": "2022-02-02T12:00:00.000Z",
    },
    {
        "items": [
            {
                "type": "CATEGORY",
                "name": "Телевизоры",
                "id": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                "parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
            },
            {
                "type": "OFFER",
                "name": 'Samson 70" LED UHD Smart',
                "id": "98883e8f-0507-482f-bce2-2fb306cf6483",
                "parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                "price": 32999,
            },
            {
                "type": "OFFER",
                "name": 'Phyllis 50" LED UHD Smarter',
                "id": "74b81fda-9cdc-4b63-8927-c978afed5cf4",
                "parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                "price": 49999,
            },
        ],
        "updateDate": "2022-02-03T12:00:00.000Z",
    },
    {
        "items": [
            {
                "type": "OFFER",
                "name": 'Goldstar 65" LED UHD LOL Very Smart',
                "id": "73bc3b36-02d1-4245-ab35-3106c9ee1c65",
                "parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                "price": 69999,
            }
        ],
        "updateDate": "2022-02-03T15:00:00.000Z",
    },
]

EXPECTED_TREE = {
    "type": "CATEGORY",
    "name": "Товары",
    "id": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
    "price": 58599,
    "parentId": None,
    "date": "2022-02-03T15:00:00.000Z",
    "children": [
        {
            "type": "CATEGORY",
            "name": "Телевизоры",
            "id": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
            "parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
            "price": 50999,
            "date": "2022-02-03T15:00:00.000Z",
            "children": [
                {
                    "type": "OFFER",
                    "name": 'Samson 70" LED UHD Smart',
                    "id": "98883e8f-0507-482f-bce2-2fb306cf6483",
                    "parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                    "price": 32999,
                    "date": "2022-02-03T12:00:00.000Z",
                    "children": None,
                },
                {
                    "type": "OFFER",
                    "name": 'Phyllis 50" LED UHD Smarter',
                    "id": "74b81fda-9cdc-4b63-8927-c978afed5cf4",
                    "parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                    "price": 49999,
                    "date": "2022-02-03T12:00:00.000Z",
                    "children": None,
                },
                {
                    "type": "OFFER",
                    "name": 'Goldstar 65" LED UHD LOL Very Smart',
                    "id": "73bc3b36-02d1-4245-ab35-3106c9ee1c65",
                    "parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                    "price": 69999,
                    "date": "2022-02-03T15:00:00.000Z",
                    "children": None,
                },
            ],
        },
        {
            "type": "CATEGORY",
            "name": "Смартфоны",
            "id": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
            "parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
            "price": 69999,
            "date": "2022-02-02T12:00:00.000Z",
            "children": [
                {
                    "type": "OFFER",
                    "name": "jPhone 13",
                    "id": "863e1a7a-1304-42ae-943b-179184c077e3",
                    "parentId": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
                    "price": 79999,
                    "date": "2022-02-02T12:00:00.000Z",
                    "children": None,
                },
                {
                    "type": "OFFER",
                    "name": "Xomiа Readme 10",
                    "id": "b1d8fd7d-2ae3-47d5-b2f9-0f094af800d4",
                    "parentId": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
                    "price": 59999,
                    "date": "2022-02-02T12:00:00.000Z",
                    "children": None,
                },
            ],
        },
    ],
}


def test_nodes():
    status, response = request(f"/nodes/{ROOT_ID}", json_response=True)

    assert status == 200, f"Expected HTTP status code 200, got {status}"

    deep_sort_children(response)
    deep_sort_children(EXPECTED_TREE)
    if response != EXPECTED_TREE:
        print_diff(EXPECTED_TREE, response)
        print("Response tree doesn't match expected tree.")
        sys.exit(1)

    print("Test nodes passed.")


def test_delete():
    status, _ = request(f"/delete/{ROOT_ID}", method="DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    status, _ = request(f"/nodes/{ROOT_ID}", json_response=True)
    assert status == 404, f"Expected HTTP status code 404, got {status}"

    print("Test delete passed.")


def test_sales():
    params = urllib.parse.urlencode({"date": "2022-02-04T00:00:00.000Z"})
    status, response = request(f"/sales?{params}", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    print("Test sales passed.")


def test_all():
    test_imports()
    test_nodes()
    test_delete()
    test_sales()


def main():
    global API_BASEURL
    test_name = None

    for arg in sys.argv[1:]:
        if re.match(r"^https?://", arg):
            API_BASEURL = arg
        elif test_name is None:
            test_name = arg

    if API_BASEURL.endswith("/"):
        API_BASEURL = API_BASEURL[:-1]

    if test_name is None:
        test_all()
    else:
        test_func = globals().get(f"test_{test_name}")
        if not test_func:
            print(f"Unknown test: {test_name}")
            sys.exit(1)
        test_func()


if __name__ == "__main__":
    main()
