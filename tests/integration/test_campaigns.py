from fastapi.testclient import TestClient


def create_test_company(client: TestClient) -> int:
    response = client.post("/companies/", json={"name": "Acme Inc"})
    assert response.status_code == 200
    return response.json()["id"]


def create_test_client(client: TestClient, company_id: int) -> int:
    response = client.post(
        "/clients/",
        json={
            "name": "Juan",
            "apellido": "Perez",
            "company_id": company_id,
        },
    )
    assert response.status_code == 200
    return response.json()["id"]


def create_test_project(client: TestClient, client_id: int) -> int:
    response = client.post(
        "/projects/",
        json={"name": "Test Project", "client_id": client_id},
    )
    assert response.status_code == 200
    return response.json()["id"]


def _create_project(client: TestClient) -> int:
    company_id = create_test_company(client)
    client_id = create_test_client(client, company_id)
    return create_test_project(client, client_id)


def _create_campaign(client: TestClient, project_id: int, number: int = 1) -> int:
    response = client.post(
        "/campaigns/",
        json={
            "project_id": project_id,
            "number": number,
            "campaign_type": "normal",
            "industry": "SaaS",
            "country": "AR",
            "company_size": "50-200",
        },
    )
    assert response.status_code == 200
    return response.json()["id"]


def _create_buyer_persona(client: TestClient, campaign_id: int) -> int:
    response = client.post(
        f"/campaigns/{campaign_id}/buyer-personas",
        json={"position": "CTO", "trigger": "hiring"},
    )
    assert response.status_code == 200
    return response.json()["id"]


def test_create_campaign(client: TestClient) -> None:
    project_id = _create_project(client)

    response = client.post(
        "/campaigns/",
        json={
            "project_id": project_id,
            "number": 1,
            "campaign_type": "normal",
            "industry": "SaaS",
            "country": "AR",
            "company_size": "50-200",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["project_id"] == project_id
    assert data["number"] == 1
    assert data["industry"] == "SaaS"
    assert data["copy_status"] == "draft"


def test_list_campaigns_by_project(client: TestClient) -> None:
    project_id = _create_project(client)
    _create_campaign(client, project_id, number=1)
    _create_campaign(client, project_id, number=2)

    response = client.get(f"/campaigns/by-project/{project_id}")

    assert response.status_code == 200
    campaigns = response.json()
    assert len(campaigns) == 2
    assert {c["number"] for c in campaigns} == {1, 2}


def test_create_buyer_persona(client: TestClient) -> None:
    project_id = _create_project(client)
    campaign_id = _create_campaign(client, project_id)

    response = client.post(
        f"/campaigns/{campaign_id}/buyer-personas",
        json={"position": "CTO", "trigger": "hiring"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["campaign_detail_id"] == campaign_id
    assert data["position"] == "CTO"
    assert data["trigger"] == "hiring"
    assert data["status"] == "draft"


def test_buyer_persona_status_update(client: TestClient) -> None:
    project_id = _create_project(client)
    campaign_id = _create_campaign(client, project_id)
    bp_id = _create_buyer_persona(client, campaign_id)

    response = client.patch(
        f"/buyer-personas/{bp_id}/status",
        json={"status": "validated"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "validated"


def test_set_lemlist_id(client: TestClient) -> None:
    project_id = _create_project(client)
    campaign_id = _create_campaign(client, project_id)
    bp_id = _create_buyer_persona(client, campaign_id)

    response = client.patch(
        f"/buyer-personas/{bp_id}/lemlist-id",
        json={"lemlist_campaign_id": "lem_abc123"},
    )

    assert response.status_code == 200
    assert response.json()["lemlist_campaign_id"] == "lem_abc123"


def test_create_sequence_and_messages(client: TestClient) -> None:
    project_id = _create_project(client)
    campaign_id = _create_campaign(client, project_id)
    bp_id = _create_buyer_persona(client, campaign_id)

    seq_response = client.post(
        f"/buyer-personas/{bp_id}/sequences",
        json={"sequence_type": "linkedin"},
    )
    assert seq_response.status_code == 200
    sequence_id = seq_response.json()["id"]

    client.post(
        f"/sequences/{sequence_id}/messages",
        json={"order": 1, "body": "Hi there", "delay_days": 0},
    )
    client.post(
        f"/sequences/{sequence_id}/messages",
        json={"order": 2, "body": "Follow up", "delay_days": 3},
    )

    response = client.get(f"/sequences/{sequence_id}/messages")
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) == 2
    messages_sorted = sorted(messages, key=lambda m: m["order"])
    assert messages_sorted[0]["body"] == "Hi there"
    assert messages_sorted[1]["body"] == "Follow up"
    assert messages_sorted[1]["delay_days"] == 3


def test_approve_message(client: TestClient) -> None:
    project_id = _create_project(client)
    campaign_id = _create_campaign(client, project_id)
    bp_id = _create_buyer_persona(client, campaign_id)
    seq_response = client.post(
        f"/buyer-personas/{bp_id}/sequences",
        json={"sequence_type": "linkedin"},
    )
    sequence_id = seq_response.json()["id"]
    msg_response = client.post(
        f"/sequences/{sequence_id}/messages",
        json={"order": 1, "body": "Hello"},
    )
    message_id = msg_response.json()["id"]

    response = client.patch(f"/messages/{message_id}/approve")

    assert response.status_code == 200
    assert response.json()["approved"] is True


def test_create_validation(client: TestClient) -> None:
    project_id = _create_project(client)
    campaign_id = _create_campaign(client, project_id)
    bp_id = _create_buyer_persona(client, campaign_id)
    seq_response = client.post(
        f"/buyer-personas/{bp_id}/sequences",
        json={"sequence_type": "linkedin"},
    )
    sequence_id = seq_response.json()["id"]
    msg_response = client.post(
        f"/sequences/{sequence_id}/messages",
        json={"order": 1, "body": "Hello"},
    )
    message_id = msg_response.json()["id"]

    response = client.post(
        f"/messages/{message_id}/validations",
        json={"author_id": 1, "text": "Looks good", "approved": True},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message_id"] == message_id
    assert data["text"] == "Looks good"
    assert data["approved"] is True


def test_full_flow(client: TestClient) -> None:
    project_id = _create_project(client)
    campaign_id = _create_campaign(client, project_id)
    bp_id = _create_buyer_persona(client, campaign_id)

    seq_response = client.post(
        f"/buyer-personas/{bp_id}/sequences",
        json={"sequence_type": "linkedin"},
    )
    sequence_id = seq_response.json()["id"]

    message_ids: list[int] = []
    for i in range(1, 3):
        msg = client.post(
            f"/sequences/{sequence_id}/messages",
            json={"order": i, "body": f"Message {i}"},
        )
        message_ids.append(msg.json()["id"])

    for mid in message_ids:
        approve = client.patch(f"/messages/{mid}/approve")
        assert approve.json()["approved"] is True

    bp_update = client.patch(
        f"/buyer-personas/{bp_id}/status",
        json={"status": "validated"},
    )
    assert bp_update.json()["status"] == "validated"

    campaign_update = client.patch(
        f"/campaigns/{campaign_id}/copy-status",
        json={"copy_status": "validated"},
    )
    assert campaign_update.status_code == 200
    assert campaign_update.json()["copy_status"] == "validated"

    final = client.get(f"/campaigns/{campaign_id}")
    assert final.json()["copy_status"] == "validated"
