import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app
from app.models.webhook import WebhookCreate, WebhookResponse

client = TestClient(app)


@pytest.fixture
def sample_webhook_data():
    return {
        "event_type": "user.created",
        "payload": {"user_id": "123", "email": "test@example.com"},
        "source": "test-service",
        "headers": {"content-type": "application/json"}
    }


@pytest.fixture
def sample_webhook_response():
    return {
        "id": "test-uuid",
        "event_type": "user.created",
        "payload": {"user_id": "123", "email": "test@example.com"},
        "source": "test-service",
        "headers": {"content-type": "application/json"},
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00",
        "processed": False,
        "processed_at": None
    }


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "Skippy"


@patch('app.services.webhook_service.WebhookService.create_webhook')
@patch('app.workers.tasks.process_webhook_task.delay')
def test_create_webhook(mock_task_delay, mock_create_webhook, sample_webhook_data, sample_webhook_response):
    """Test creating a webhook."""
    mock_create_webhook.return_value = WebhookResponse(**sample_webhook_response)
    mock_task_delay.return_value = None
    
    response = client.post("/webhooks", json=sample_webhook_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["event_type"] == sample_webhook_data["event_type"]
    assert data["payload"] == sample_webhook_data["payload"]
    assert data["source"] == sample_webhook_data["source"]
    
    mock_create_webhook.assert_called_once()
    mock_task_delay.assert_called_once_with(data["id"])


@patch('app.services.webhook_service.WebhookService.list_webhooks')
def test_list_webhooks(mock_list_webhooks, sample_webhook_response):
    """Test listing webhooks."""
    mock_list_webhooks.return_value = [WebhookResponse(**sample_webhook_response)]
    
    response = client.get("/webhooks")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["event_type"] == sample_webhook_response["event_type"]


@patch('app.services.webhook_service.WebhookService.get_webhook')
def test_get_webhook(mock_get_webhook, sample_webhook_response):
    """Test getting a specific webhook."""
    mock_get_webhook.return_value = WebhookResponse(**sample_webhook_response)
    
    response = client.get("/webhooks/test-uuid")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test-uuid"
    assert data["event_type"] == sample_webhook_response["event_type"]


@patch('app.services.webhook_service.WebhookService.get_webhook')
def test_get_webhook_not_found(mock_get_webhook):
    """Test getting a non-existent webhook."""
    mock_get_webhook.return_value = None
    
    response = client.get("/webhooks/non-existent")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Webhook not found"


@patch('app.services.webhook_service.WebhookService.update_webhook')
def test_update_webhook(mock_update_webhook, sample_webhook_response):
    """Test updating a webhook."""
    updated_response = sample_webhook_response.copy()
    updated_response["event_type"] = "user.updated"
    mock_update_webhook.return_value = WebhookResponse(**updated_response)
    
    update_data = {"event_type": "user.updated"}
    response = client.put("/webhooks/test-uuid", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["event_type"] == "user.updated"


@patch('app.services.webhook_service.WebhookService.delete_webhook')
def test_delete_webhook(mock_delete_webhook):
    """Test deleting a webhook."""
    mock_delete_webhook.return_value = True
    
    response = client.delete("/webhooks/test-uuid")
    
    assert response.status_code == 200
    assert response.json()["message"] == "Webhook deleted successfully"


@patch('app.services.webhook_service.WebhookService.delete_webhook')
def test_delete_webhook_not_found(mock_delete_webhook):
    """Test deleting a non-existent webhook."""
    mock_delete_webhook.return_value = False
    
    response = client.delete("/webhooks/non-existent")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Webhook not found"


@patch('app.services.webhook_service.WebhookService.get_webhook')
@patch('app.workers.tasks.process_webhook_task.delay')
def test_process_webhook(mock_task_delay, mock_get_webhook, sample_webhook_response):
    """Test manually triggering webhook processing."""
    mock_get_webhook.return_value = WebhookResponse(**sample_webhook_response)
    mock_task_delay.return_value = None
    
    response = client.post("/webhooks/test-uuid/process")
    
    assert response.status_code == 200
    assert response.json()["message"] == "Webhook queued for processing"
    mock_task_delay.assert_called_once_with("test-uuid")
