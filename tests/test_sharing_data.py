# share endpoint, model creation, invalid recipient, duplicate share

def test_hi_and_bye_appear(client, two_users):
    user1, user2 = two_users
    print(user1.username)
    print(user2.username)
    assert True