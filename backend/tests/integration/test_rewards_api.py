from fastapi.testclient import TestClient
from backend.main import app
from backend.store import store

client = TestClient(app)


class TestRewardsAPI:
    def test_rewards_status_default(self):
        r = client.get("/api/rewards/status?student_id=99")
        assert r.status_code == 200
        data = r.json()
        assert data["level"] == 1
        assert data["star_coins"] == 0
        assert data["streak_days"] == 0

    def test_process_reward_correct(self):
        r = client.post("/api/rewards/process?student_id=100&is_correct=true&combo=1")
        assert r.status_code == 200
        data = r.json()
        assert data["xp_earned"] >= 10
        assert "sprite_reaction" in data

    def test_process_reward_wrong(self):
        r = client.post("/api/rewards/process?student_id=101&is_correct=false&combo=0")
        assert r.status_code == 200
        data = r.json()
        assert data["xp_earned"] == 0
        assert data["sprite_reaction"] in ("encourage", "thinking")

    def test_process_reward_achievement(self):
        store.clear_achievements(102)
        r = client.post("/api/rewards/process?student_id=102&is_correct=true&combo=1")
        assert r.status_code == 200
        data = r.json()
        assert data["achievement_unlocked"] == "first_correct"

    def test_process_reward_level_up(self):
        for i in range(10):
            client.post(f"/api/rewards/process?student_id=103&is_correct=true&combo=3&time_spent=2")
        r = client.get("/api/rewards/status?student_id=103")
        data = r.json()
        assert data["level"] >= 2


class TestSpriteAPI:
    def test_sprite_state_default(self):
        r = client.get("/api/sprite/state?student_id=10")
        assert r.status_code == 200
        data = r.json()
        assert data["stage"] == 0
        assert data["stage_name"] == "星尘"
        assert "progress" in data

    def test_sprite_customize(self):
        r = client.post("/api/sprite/customize?student_id=10", json={"skin": "deep_blue"})
        assert r.status_code == 200
        assert r.json()["skin"] == "deep_blue"
