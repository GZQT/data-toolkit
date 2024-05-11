def test_health(request):
    client = request.getfixturevalue('create_test_db')
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'
