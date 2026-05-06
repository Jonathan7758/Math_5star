from fastapi.testclient import TestClient
from backend.main import app
from backend.config import KNOWLEDGE_GRAPH_PATH, QUIZ_BANK_PATH

client = TestClient(app)


class TestDiagnoseAPI:
    def test_diagnose_success(self):
        response = client.post("/api/diagnose", json={
            "student_id": 1,
            "records": [
                {"kp_id": "K03", "is_correct": False},
                {"kp_id": "K07", "is_correct": True},
            ],
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "root_causes" in data
        assert data["total_records"] == 2
        assert data["incorrect_count"] == 1

    def test_diagnose_empty_body(self):
        response = client.post("/api/diagnose", json={})
        assert response.status_code == 422

    def test_diagnose_empty_records(self):
        response = client.post("/api/diagnose", json={
            "student_id": 1,
            "records": [],
        })
        assert response.status_code == 400

    def test_diagnose_all_correct(self):
        response = client.post("/api/diagnose", json={
            "student_id": 1,
            "records": [
                {"kp_id": "K01", "is_correct": True},
                {"kp_id": "K02", "is_correct": True},
            ],
        })
        assert response.status_code == 200
        data = response.json()
        assert data["root_causes"] == []

    def test_diagnose_root_cause_structure(self):
        response = client.post("/api/diagnose", json={
            "student_id": 1,
            "records": [
                {"kp_id": "K03", "is_correct": False},
            ],
        })
        assert response.status_code == 200
        data = response.json()
        for rc in data["root_causes"]:
            assert "kp_id" in rc
            assert "kp_name" in rc
            assert "priority" in rc
            assert "reason" in rc
            assert isinstance(rc["priority"], (int, float))

    def test_diagnose_with_k03_errors(self):
        response = client.post("/api/diagnose", json={
            "student_id": 1,
            "records": [
                {"kp_id": "K03", "is_correct": False},
                {"kp_id": "K03", "is_correct": False},
                {"kp_id": "K03", "is_correct": False},
            ],
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data["root_causes"]) > 0
        root_ids = [rc["kp_id"] for rc in data["root_causes"]]
        assert "K01" in root_ids or "K02" in root_ids


class TestExerciseAPI:
    def test_get_next_question(self):
        response = client.get("/api/exercise/next?student_id=1")
        assert response.status_code == 200
        data = response.json()
        assert "question_id" in data
        assert "question" in data
        assert "knowledge_point_id" in data

    def test_get_next_question_by_kp(self):
        response = client.get("/api/exercise/next?student_id=1&kp_id=K01")
        assert response.status_code == 200
        data = response.json()
        assert data["knowledge_point_id"] == "K01"

    def test_submit_correct_answer(self):
        response = client.post("/api/exercise/submit", json={
            "student_id": 1,
            "question_id": "Q-K01-L1-01",
            "answer": "7",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["is_correct"] is True
        assert data["xp_earned"] == 10

    def test_submit_wrong_answer(self):
        response = client.post("/api/exercise/submit", json={
            "student_id": 1,
            "question_id": "Q-K01-L1-01",
            "answer": "99",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["is_correct"] is False
        assert data["xp_earned"] == 0
        assert data["hint"] is not None

    def test_submit_equivalent_answer(self):
        response = client.post("/api/exercise/submit", json={
            "student_id": 1,
            "question_id": "Q-K02-L2-01",
            "answer": "0.75",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["is_correct"] is True

    def test_submit_unknown_question(self):
        response = client.post("/api/exercise/submit", json={
            "student_id": 1,
            "question_id": "non-existent",
            "answer": "0",
        })
        assert response.status_code == 404
