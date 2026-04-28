from datetime import datetime


def test_saved_routes_and_lifecycle(client, app_env):
    module = app_env["module"]

    first_id = module.intel_db.save_item({
        "title": "First",
        "url": "https://example.com/first",
        "source": "GitHub Trending",
        "source_type": "github",
        "status": "to_read",
        "signal_score": 80,
    })
    second_id = module.intel_db.save_item({
        "title": "Second",
        "url": "https://example.com/second",
        "source": "GitHub Trending",
        "source_type": "github",
        "status": "to_read",
        "signal_score": 70,
    })

    status_response = client.put(f"/api/saved/{first_id}/status", json={"status": "useful"})
    assert status_response.status_code == 200
    items = {item["id"]: item for item in module.intel_db.get_saved_items()}
    assert items[first_id]["status"] == "useful"
    assert items[second_id]["status"] == "to_read"

    notes_response = client.put(f"/api/saved/{first_id}/notes", json={"notes": "important", "tags": ["agent", "pi"]})
    assert notes_response.status_code == 200
    items = {item["id"]: item for item in module.intel_db.get_saved_items()}
    assert items[first_id]["notes"] == "important"
    assert items[first_id]["tags"] == ["agent", "pi"]
    assert items[second_id]["notes"] == ""

    delete_response = client.delete(f"/api/saved/{first_id}")
    assert delete_response.status_code == 200
    remaining_ids = {item["id"] for item in module.intel_db.get_saved_items()}
    assert first_id not in remaining_ids
    assert second_id in remaining_ids


def test_track_routes_and_malformed_routes(client, app_env):
    module = app_env["module"]

    assert client.post("/api/track", json={"topic": "agents", "reason": "keep watching"}).status_code == 200
    assert client.post("/api/track", json={"topic": "local-llm", "reason": "pi testing"}).status_code == 200

    topics = client.get("/api/track").get_json()["topics"]
    tracked = {topic["topic"]: topic["id"] for topic in topics}
    assert "agents" in tracked
    assert "local-llm" in tracked

    delete_response = client.delete(f"/api/track/{tracked['agents']}")
    assert delete_response.status_code == 200

    remaining = {topic["topic"] for topic in client.get("/api/track").get_json()["topics"]}
    assert "agents" not in remaining
    assert "local-llm" in remaining

    assert client.open("/api/saved/", method="DELETE").status_code == 404
    assert client.open("/api/saved//status", method="PUT").status_code == 404
    assert client.open("/api/saved//notes", method="PUT").status_code == 404
    assert client.open("/api/track/", method="DELETE").status_code == 404


def test_save_ignore_and_digest_routes(client, app_env):
    save_response = client.post(
        "/api/save",
        json={
            "title": "Saved from API",
            "url": "https://example.com/saved",
            "source": "GitHub Trending",
            "source_type": "github",
            "category": "agents",
            "signal_score": 91,
        },
    )
    assert save_response.status_code == 200
    item_id = save_response.get_json()["id"]

    saved_items = client.get("/api/saved").get_json()["items"]
    assert any(item["id"] == item_id for item in saved_items)

    ignore_response = client.post(
        "/api/ignore",
        json={"url": "https://example.com/ignore", "title": "Ignore Me", "source_type": "blogs"},
    )
    assert ignore_response.status_code == 200
    ignored_items = client.get("/api/ignored").get_json()["items"]
    assert any(item["url"] == "https://example.com/ignore" for item in ignored_items)

    digest_response = client.get("/api/digest")
    assert digest_response.status_code == 200
    payload = digest_response.get_json()
    digest = payload["digest"]
    assert "AI Intelligence" in digest
    assert payload["path"].endswith(".md")
    digest_path = app_env["digest_dir"] / f"{datetime.now().strftime('%Y-%m-%d')}.md"
    assert digest_path.exists()


def test_refresh_endpoint_success_and_failure_preserves_data(client, app_env, monkeypatch):
    import json
    import fetch_news

    def successful_refresh():
        data_file = app_env["data_dir"] / "data.json"
        data = json.loads(data_file.read_text(encoding="utf-8"))
        data["last_updated"] = datetime.now().isoformat()
        data_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        app_env["module"].intel_db.update_source_health("github", True, item_count=1)

    monkeypatch.setattr(fetch_news, "fetch_all", successful_refresh)
    refresh_response = client.post("/api/refresh")
    assert refresh_response.status_code == 200
    refresh_payload = refresh_response.get_json()
    assert refresh_payload["status"] in {"ok", "partial", "failed"}
    assert "source_health" in refresh_payload
    assert "message" in refresh_payload

    original_data = (app_env["data_dir"] / "data.json").read_text(encoding="utf-8")

    def fail_refresh():
        raise RuntimeError("network unavailable")

    monkeypatch.setattr(fetch_news, "fetch_all", fail_refresh)
    failure_response = client.post("/api/refresh")
    failure_payload = failure_response.get_json()
    assert failure_response.status_code == 200
    assert failure_payload["status"] == "failed"
    assert "Existing data preserved" in failure_payload["message"]
    assert (app_env["data_dir"] / "data.json").read_text(encoding="utf-8") == original_data


def test_dashboard_meta_snapshot(client, app_env):
    module = app_env["module"]
    module.intel_db.update_source_health("github", True, item_count=3)

    response = client.get("/api/dashboard-meta")
    assert response.status_code == 200

    payload = response.get_json()
    assert payload["snapshot_id"]
    assert "last_updated_display" in payload
    assert "daily_summary" in payload
    assert "counts" in payload
