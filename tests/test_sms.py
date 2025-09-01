import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app
from app.models.sms import SMSWebhook, SMSResponse

client = TestClient(app)


@pytest.fixture
def sample_sms_webhook_data():
    return {
        "id": "sf8425555e5d8db61dda7a7b3f1b91bdb",
        "from": "+46706861004",
        "to": "+46706860000",
        "message": "Hello how are you?",
        "direction": "incoming",
        "created": "2018-07-13T13:57:23.741000"
    }


@pytest.fixture
def sample_sms_response():
    return {
        "id": "sf8425555e5d8db61dda7a7b3f1b91bdb",
        "from_number": "+46706861004",
        "to_number": "+46706860000",
        "message": "Hello how are you?",
        "direction": "incoming",
        "created": "2018-07-13T13:57:23.741000",
        "processed": False,
        "processed_at": None,
        "reply_sent": False,
        "reply_message": None
    }


@patch('app.services.sms_service.SMSService.store_sms')
@patch('app.workers.sms_tasks.process_sms_task.delay')
def test_receive_sms_webhook(mock_task_delay, mock_store_sms, sample_sms_webhook_data, sample_sms_response):
    """Test receiving SMS webhook from 46elks."""
    mock_store_sms.return_value = SMSResponse(**sample_sms_response)
    mock_task_delay.return_value = None
    
    # Simulate form data from 46elks
    form_data = {
        "id": sample_sms_webhook_data["id"],
        "from": sample_sms_webhook_data["from"],
        "to": sample_sms_webhook_data["to"],
        "message": sample_sms_webhook_data["message"],
        "direction": sample_sms_webhook_data["direction"],
        "created": sample_sms_webhook_data["created"]
    }
    
    response = client.post("/elks/sms", data=form_data)
    
    assert response.status_code == 200
    assert "Thank you for your message" in response.text
    
    mock_store_sms.assert_called_once()
    mock_task_delay.assert_called_once_with(sample_sms_webhook_data["id"])


@patch('app.services.sms_service.SMSService.list_sms')
def test_list_sms(mock_list_sms, sample_sms_response):
    """Test listing SMS messages."""
    mock_list_sms.return_value = [SMSResponse(**sample_sms_response)]
    
    response = client.get("/sms")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["from_number"] == sample_sms_response["from_number"]


@patch('app.services.sms_service.SMSService.get_sms')
def test_get_sms(mock_get_sms, sample_sms_response):
    """Test getting a specific SMS."""
    mock_get_sms.return_value = SMSResponse(**sample_sms_response)
    
    response = client.get("/sms/sf8425555e5d8db61dda7a7b3f1b91bdb")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "sf8425555e5d8db61dda7a7b3f1b91bdb"
    assert data["message"] == "Hello how are you?"


@patch('app.services.sms_service.SMSService.get_sms')
def test_get_sms_not_found(mock_get_sms):
    """Test getting a non-existent SMS."""
    mock_get_sms.return_value = None
    
    response = client.get("/sms/non-existent")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "SMS not found"


@patch('app.services.sms_service.SMSService.get_sms')
@patch('app.services.sms_service.SMSService.mark_reply_sent')
@patch('app.workers.sms_tasks.send_sms_reply_task.delay')
def test_send_sms_reply(mock_task_delay, mock_mark_reply, mock_get_sms, sample_sms_response):
    """Test sending an SMS reply."""
    mock_get_sms.return_value = SMSResponse(**sample_sms_response)
    mock_mark_reply.return_value = None
    mock_task_delay.return_value = None
    
    reply_data = {
        "message": "Thanks for your message!",
        "to_number": "+46706861004"
    }
    
    response = client.post("/sms/sf8425555e5d8db61dda7a7b3f1b91bdb/reply", json=reply_data)
    
    assert response.status_code == 200
    assert response.json()["message"] == "SMS reply queued for sending"
    
    mock_task_delay.assert_called_once_with(
        "sf8425555e5d8db61dda7a7b3f1b91bdb",
        "Thanks for your message!",
        "+46706861004"
    )


@patch('app.services.sms_service.SMSService.delete_sms')
def test_delete_sms(mock_delete_sms):
    """Test deleting an SMS."""
    mock_delete_sms.return_value = True
    
    response = client.delete("/sms/sf8425555e5d8db61dda7a7b3f1b91bdb")
    
    assert response.status_code == 200
    assert response.json()["message"] == "SMS deleted successfully"


@patch('app.services.sms_service.SMSService.delete_sms')
def test_delete_sms_not_found(mock_delete_sms):
    """Test deleting a non-existent SMS."""
    mock_delete_sms.return_value = False
    
    response = client.delete("/sms/non-existent")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "SMS not found"
