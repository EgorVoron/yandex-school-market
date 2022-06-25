from tests.test_utils import request


def test_scenario_atomicity():
    status, _ = request("/imports", "POST", data={
        "updateDate": "2022-02-01T12:00:00.000Z",
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
    assert status == 200
    status, result = request("/nodes/offer1", "GET")
    assert status == 404
    status, result = request("/nodes/offer2", "GET")
    assert status == 404
    status, result = request("/nodes/offer3", "GET")
    assert status == 404
    print("Atomicity test passed")


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


if __name__ == "__main__":
    test_all()
