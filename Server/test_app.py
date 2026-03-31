import pytest
from datetime import datetime
from app import app, device_list, Device, token


@pytest.fixture
def client():
    """Create a Flask test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def reset_device_list():
    """Reset device_list before each test."""
    global device_list, token
    original_devices = device_list.copy()
    original_token = token
    device_list = {
        'Windows': Device('💻电脑'),
        'Android': Device('📱手机'),
    }
    token = 'test_token'
    yield
    device_list = original_devices
    token = original_token


class TestUpdateFunction:
    """Test suite for the /api/update endpoint."""

    def test_update_success_with_valid_device(self, client):
        """Test successful update with valid device name and all parameters."""
        response = client.post('/api/update', data={
            'token': 'test_token',
            'device_name': 'Windows',
            'program_name': 'VS Code',
            'extra_data': 'Working on unit tests'
        })
        
        assert response.status_code == 200
        assert response.json['message'] == 'Updated data of device Windows'
        assert device_list['Windows'].program_name == 'VS Code'
        assert device_list['Windows'].extra_data == 'Working on unit tests'

    def test_update_success_with_empty_extra_data(self, client):
        """Test successful update with empty extra_data."""
        response = client.post('/api/update', data={
            'token': 'test_token',
            'device_name': 'Android',
            'program_name': 'Chrome',
            'extra_data': ''
        })
        
        assert response.status_code == 200
        assert response.json['message'] == 'Updated data of device Android'
        assert device_list['Android'].program_name == 'Chrome'
        assert device_list['Android'].extra_data == ''

    def test_update_without_extra_data(self, client):
        """Test successful update without providing extra_data parameter."""
        # Note: This will fail due to required_params decorator, but testing behavior
        original_device = Device('Windows')
        original_time = device_list['Windows'].time_last_updated
        
        response = client.post('/api/update', data={
            'token': 'test_token',
            'device_name': 'Windows',
            'program_name': 'Notepad'
        })
        
        # required_params decorator should return 400 for missing extra_data if it were required
        # But looking at the decorator, it only checks 'device_name' and 'program_name'
        # So this should work
        assert response.status_code == 200
        assert response.json['message'] == 'Updated data of device Windows'

    def test_update_with_invalid_device_name(self, client):
        """Test update with non-existent device name returns 400 error."""
        response = client.post('/api/update', data={
            'token': 'test_token',
            'device_name': 'iOS',
            'program_name': 'Safari'
        })
        
        assert response.status_code == 400
        assert response.json['error'] == 'Invalid device name'

    def test_update_without_token(self, client):
        """Test update without token returns 401 error."""
        response = client.post('/api/update', data={
            'device_name': 'Windows',
            'program_name': 'VS Code'
        })
        
        assert response.status_code == 401
        assert response.json['error'] == 'Verification failed'

    def test_update_with_wrong_token(self, client):
        """Test update with incorrect token returns 401 error."""
        response = client.post('/api/update', data={
            'token': 'wrong_token',
            'device_name': 'Windows',
            'program_name': 'VS Code'
        })
        
        assert response.status_code == 401
        assert response.json['error'] == 'Verification failed'

    def test_update_without_device_name(self, client):
        """Test update without device_name parameter returns 400 error."""
        response = client.post('/api/update', data={
            'token': 'test_token',
            'program_name': 'VS Code'
        })
        
        assert response.status_code == 400
        assert response.json['error'] == 'Invalid argument'

    def test_update_without_program_name(self, client):
        """Test update without program_name parameter returns 400 error."""
        response = client.post('/api/update', data={
            'token': 'test_token',
            'device_name': 'Windows'
        })
        
        assert response.status_code == 400
        assert response.json['error'] == 'Invalid argument'

    def test_update_updates_timestamp(self, client):
        """Test that update correctly updates the device timestamp."""
        original_time = device_list['Windows'].time_last_updated
        
        # Small delay to ensure timestamp difference
        import time
        time.sleep(0.01)
        
        response = client.post('/api/update', data={
            'token': 'test_token',
            'device_name': 'Windows',
            'program_name': 'New Program'
        })
        
        assert response.status_code == 200
        assert device_list['Windows'].time_last_updated > original_time

    def test_update_multiple_devices(self, client):
        """Test updating multiple devices independently."""
        # Update first device
        response1 = client.post('/api/update', data={
            'token': 'test_token',
            'device_name': 'Windows',
            'program_name': 'VS Code'
        })
        assert response1.status_code == 200
        
        # Update second device
        response2 = client.post('/api/update', data={
            'token': 'test_token',
            'device_name': 'Android',
            'program_name': 'Chrome',
            'extra_data': 'Browsing'
        })
        assert response2.status_code == 200
        
        # Verify both devices have correct data
        assert device_list['Windows'].program_name == 'VS Code'
        assert device_list['Android'].program_name == 'Chrome'
        assert device_list['Android'].extra_data == 'Browsing'

    def test_update_with_special_characters_in_program_name(self, client):
        """Test update with special characters in program_name."""
        response = client.post('/api/update', data={
            'token': 'test_token',
            'device_name': 'Windows',
            'program_name': 'Visual Studio Code (Insiders) @work',
            'extra_data': 'Project: PeekMe <v2.0>'
        })
        
        assert response.status_code == 200
        assert device_list['Windows'].program_name == 'Visual Studio Code (Insiders) @work'
        assert device_list['Windows'].extra_data == 'Project: PeekMe <v2.0>'

    def test_update_with_very_long_program_name(self, client):
        """Test update with extremely long program name."""
        long_name = 'A' * 1000
        response = client.post('/api/update', data={
            'token': 'test_token',
            'device_name': 'Windows',
            'program_name': long_name,
            'extra_data': 'Testing edge case'
        })
        
        assert response.status_code == 200
        assert device_list['Windows'].program_name == long_name

    def test_update_preserves_device_online_state(self, client):
        """Test that update doesn't change device online state."""
        original_online_state = device_list['Windows'].online
        
        response = client.post('/api/update', data={
            'token': 'test_token',
            'device_name': 'Windows',
            'program_name': 'New App'
        })
        
        assert response.status_code == 200
        assert device_list['Windows'].online == original_online_state

    def test_update_overwrites_previous_data(self, client):
        """Test that update overwrites previous program_name and extra_data."""
        # First update
        response1 = client.post('/api/update', data={
            'token': 'test_token',
            'device_name': 'Windows',
            'program_name': 'App1',
            'extra_data': 'Data1'
        })
        assert response1.status_code == 200
        
        # Second update - should overwrite
        response2 = client.post('/api/update', data={
            'token': 'test_token',
            'device_name': 'Windows',
            'program_name': 'App2',
            'extra_data': 'Data2'
        })
        assert response2.status_code == 200
        
        # Verify overwritten
        assert device_list['Windows'].program_name == 'App2'
        assert device_list['Windows'].extra_data == 'Data2'

    def test_update_case_sensitive_device_name(self, client):
        """Test that device name matching is case-sensitive."""
        response = client.post('/api/update', data={
            'token': 'test_token',
            'device_name': 'windows',  # lowercase
            'program_name': 'Test'
        })
        
        # Should fail as 'windows' != 'Windows'
        assert response.status_code == 400
        assert response.json['error'] == 'Invalid device name'

    def test_update_with_unicode_characters(self, client):
        """Test update with Unicode characters in extra_data."""
        response = client.post('/api/update', data={
            'token': 'test_token',
            'device_name': 'Android',
            'program_name': '微信',
            'extra_data': '正在测试中文和日本語和한국어'
        })
        
        assert response.status_code == 200
        assert device_list['Android'].program_name == '微信'
        assert device_list['Android'].extra_data == '正在测试中文和日本語和한국어'
