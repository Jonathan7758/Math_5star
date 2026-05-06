from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


class TestPlanAPI:
    def test_plan_success(self):
        response = client.post("/api/plan", json={
            "student_id": 1,
            "root_causes": [
                {"kp_id": "K03", "kp_name": "Rational Number Operations", "priority": 0.8, "impacted_nodes": ["K03", "K07"]},
            ],
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["path"]) >= 1
        assert "estimated_sessions" in data
        assert "summary" in data

    def test_plan_empty_causes(self):
        response = client.post("/api/plan", json={
            "student_id": 1,
            "root_causes": [],
        })
        assert response.status_code == 400

    def test_plan_path_structure(self):
        response = client.post("/api/plan", json={
            "student_id": 1,
            "root_causes": [
                {"kp_id": "K03", "kp_name": "Rational Op", "priority": 0.8, "impacted_nodes": ["K03"]},
            ],
        })
        data = response.json()
        for node in data["path"]:
            assert "order" in node
            assert "kp_id" in node
            assert "kp_name" in node
            assert "reason" in node
            assert isinstance(node["order"], int)

    def test_plan_prerequisite_order(self):
        response = client.post("/api/plan", json={
            "student_id": 1,
            "root_causes": [
                {"kp_id": "K03", "kp_name": "Rational Op", "priority": 0.8, "impacted_nodes": ["K03"]},
            ],
        })
        data = response.json()
        ids = [n["kp_id"] for n in data["path"]]
        if "K01" in ids and "K03" in ids:
            assert ids.index("K01") < ids.index("K03")
        if "K02" in ids and "K03" in ids:
            assert ids.index("K02") < ids.index("K03")

    def test_plan_multiple_root_causes(self):
        response = client.post("/api/plan", json={
            "student_id": 1,
            "root_causes": [
                {"kp_id": "K03", "kp_name": "Rational Op", "priority": 0.8, "impacted_nodes": ["K03", "K07"]},
                {"kp_id": "K05", "kp_name": "Percentages", "priority": 0.6, "impacted_nodes": ["K05"]},
            ],
        })
        data = response.json()
        assert len(data["path"]) >= 3

    def test_plan_handles_unknown_kp(self):
        response = client.post("/api/plan", json={
            "student_id": 1,
            "root_causes": [
                {"kp_id": "ZZZ", "kp_name": "Unknown", "priority": 0.5, "impacted_nodes": []},
            ],
        })
        assert response.status_code == 200
        data = response.json()
        assert "path" in data


class TestExerciseHintsAPI:
    def test_submit_with_hints_level_0(self):
        response = client.post("/api/exercise/submit", json={
            "student_id": 1,
            "question_id": "Q-K01-L1-01",
            "answer": "99",
            "hint_level_used": 0,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["is_correct"] is False
        assert data["hint_level"] == 1
        assert data["should_retry"] is True

    def test_submit_with_hints_level_1(self):
        response = client.post("/api/exercise/submit", json={
            "student_id": 1,
            "question_id": "Q-K01-L1-01",
            "answer": "99",
            "hint_level_used": 1,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["hint_level"] >= 2

    def test_submit_correct_after_hints(self):
        response = client.post("/api/exercise/submit", json={
            "student_id": 1,
            "question_id": "Q-K01-L1-01",
            "answer": "7",
            "hint_level_used": 1,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["is_correct"] is True
        assert data["xp_earned"] == 10
        assert data["hint_level"] == 0
