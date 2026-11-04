import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database.session import init_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

def test_health_endpoint():
    """Tests /api/health endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "hardware" in data
    assert "opencv_version" in data
    assert "pytorch_version" in data

def test_settings_endpoint():
    """Tests /api/settings endpoint."""
    response = client.get("/api/settings")
    assert response.status_code == 200
    data = response.json()
    assert "device" in data
    assert "default_confidence" in data
    assert "min_track_length" in data

def test_dashboard_summary_endpoint():
    """Tests /api/dashboard/summary endpoint."""
    response = client.get("/api/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_videos" in data
    assert "total_entrance_activity" in data
    assert "device_info" in data

def test_invalid_video_upload_rejection():
    """Tests that non-video files are rejected with 400 Bad Request."""
    fake_file = ("script.exe", b"invalid binary content", "application/octet-stream")
    response = client.post("/api/videos/upload", files={"file": fake_file})
    assert response.status_code == 400
    assert "Unsupported video format" in response.json()["detail"]

def test_valid_video_upload():
    """Tests uploading the generated sample synthetic video."""
    sample_path = "sample_videos/entrance_sample.mp4"
    if not os.path.exists(sample_path):
        pytest.skip("Sample video not generated yet")

    with open(sample_path, "rb") as f:
        response = client.post(
            "/api/videos/upload",
            files={"file": ("test_hive.mp4", f, "video/mp4")}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["original_filename"] == "test_hive.mp4"
    assert data["duration_sec"] > 0
    assert data["width"] == 640
    assert data["height"] == 360
    assert "id" in data
    video_id = data["id"]

    # Verify listing
    list_resp = client.get("/api/videos")
    assert list_resp.status_code == 200
    videos = list_resp.json()
    assert any(v["id"] == video_id for v in videos)

    # Verify preview frame
    preview_resp = client.get(f"/api/videos/{video_id}/preview?frame_number=10")
    assert preview_resp.status_code == 200
    assert "preview_url" in preview_resp.json()

    # Clean up test video
    del_resp = client.delete(f"/api/videos/{video_id}")
    assert del_resp.status_code == 200
