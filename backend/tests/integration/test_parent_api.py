from fastapi.testclient import TestClient
from backend.main import app
from backend.routers.parent import update_mastery, set_learning_path, add_weekly_stat

client = TestClient(app)


class TestParentAPI:
    def test_dashboard_no_pin(self):
        r = client.get("/api/parent/dashboard?student_id=1")
        assert r.status_code == 403

    def test_dashboard_wrong_pin(self):
        r = client.get("/api/parent/dashboard?student_id=1", headers={"x-parent-pin": "wrong"})
        assert r.status_code == 403

    def test_dashboard_success(self):
        update_mastery(1, "K01", True)
        update_mastery(1, "K01", False)
        update_mastery(1, "K02", True)
        add_weekly_stat(1, "2026-05-01", 15.0, 0.8, 10)
        add_weekly_stat(1, "2026-05-02", 12.5, 0.9, 8)
        set_learning_path(1, [
            {"order": 1, "kp_id": "K01", "kp_name": "Integers", "reason": "root"},
            {"order": 2, "kp_id": "K02", "kp_name": "Fractions", "reason": "next"},
        ])

        r = client.get("/api/parent/dashboard?student_id=1", headers={"x-parent-pin": "1234"})
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert len(data["mastery_heatmap"]) >= 2
        assert len(data["weekly_stats"]) == 2
        assert len(data["current_path"]) == 2
        assert len(data["suggestions"]) >= 0

    def test_dashboard_mastery_scores(self):
        update_mastery(2, "K01", True)
        update_mastery(2, "K01", True)
        update_mastery(2, "K01", False)
        r = client.get("/api/parent/dashboard?student_id=2", headers={"x-parent-pin": "1234"})
        data = r.json()
        k01 = next((h for h in data["mastery_heatmap"] if h["kp_id"] == "K01"), None)
        assert k01 is not None
        assert k01["score"] > 0.5

    def test_approve_path_no_pin(self):
        r = client.post("/api/parent/approve-path?student_id=1", json={})
        assert r.status_code == 403

    def test_approve_path_success(self):
        set_learning_path(3, [
            {"order": 1, "kp_id": "K01", "kp_name": "A", "reason": ""},
            {"order": 2, "kp_id": "K02", "kp_name": "B", "reason": ""},
        ])
        r = client.post("/api/parent/approve-path?student_id=3", json={"adjustments": {"K02": 0}}, headers={"x-parent-pin": "1234"})
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert data["path"][0]["kp_id"] == "K02"
