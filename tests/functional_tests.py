from tests.test_utils import request


def test_scenario_atomicity():
    status, _ = request("/imports", "POST", data={
        "updateDate": "2022-05-28T21:12:01.000Z",
        "items": [
            {
                "id": "offer1",
                "name": "a",
                "type": "OFFER",
                "parentId": None,
                "price": 1
            },
            {
                "id": "offer2",
                "name": "b",
                "type": "OFFER",
                "parentId": None,
                "price": 1
            },
            {
                "id": "offer3",
                "type": "OFFER",
                "parentId": None,
                "price": 1
            }
        ]
    })
    assert status == 400
    status, result = request("/nodes/offer1", "GET")
    assert status == 404
    status, result = request("/nodes/offer2", "GET")
    assert status == 404
    status, result = request("/nodes/offer3", "GET")
    assert status == 404
    print("Atomicity test passed")


def test_scenario_parents():
    status, _ = request("/imports", "POST", data={
        "updateDate": "2022-05-28T21:12:01.000Z",
        "items": [
            {
                "id": "root1",
                "name": "a",
                "type": "CATEGORY",
                "parentId": None,
                "price": None
            },
            {
                "id": "root2",
                "name": "b",
                "type": "OFFER",
                "parentId": None,
                "price": 1
            },
            {
                "id": "subroot1.1",
                "type": "OFFER",
                "parentId": "root1",
                "price": 1
            }
        ]
    })
    assert status == 200
    print("Parents test passed")

# def test_scenario_1():
#     request("/imports", "POST", data=[
#         {
#             "id": "root1",
#             "name": "a",
#             "type": "CATEGORY",
#             "parentId": None,
#             "price": None
#         },
#         {
#             "id": "subroot1",
#             "name": "b",
#             "type": "CATEGORY",
#             "parentId": "root1",
#         }
#     ])

def test_all():
    test_scenario_atomicity()
    test_scenario_parents()


if __name__ == "__main__":
    test_all()
