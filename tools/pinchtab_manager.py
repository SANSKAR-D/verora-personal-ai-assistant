import os
import requests
from dotenv import load_dotenv

load_dotenv()

PINCHTAB_URL = "http://localhost:9867"
PINCHTAB_TOKEN = os.environ.get("PINCHTAB_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {PINCHTAB_TOKEN}",
    "Content-Type": "application/json",
}

# Global state — shared across all browser tools
_instance_id = None
_tab_id = None


def api_get(path: str, params: dict = None) -> dict:
    """Makes a GET request to the PinchTab API."""
    resp = requests.get(f"{PINCHTAB_URL}{path}", headers=HEADERS, params=params)
    return resp.json()


def api_post(path: str, body: dict) -> dict:
    """Makes a POST request to the PinchTab API."""
    resp = requests.post(f"{PINCHTAB_URL}{path}", headers=HEADERS, json=body)
    return resp.json()


def get_instance_id() -> str:
    """Returns a running instance ID. Reuses existing instance or starts a new headed one."""
    global _instance_id
    if _instance_id:
        return _instance_id

    # First, check if there's already a running instance we can reuse
    try:
        instances = requests.get(f"{PINCHTAB_URL}/instances", headers=HEADERS).json()
        instance_list = []
        if isinstance(instances, dict) and instances.get("id"):
            instance_list = [instances]
        elif isinstance(instances, list):
            instance_list = instances

        for inst in instance_list:
            if inst.get("status") == "running":
                # If it's headless, we need to stop it so we can start a headed one
                if inst.get("headless") == True or inst.get("mode") == "headless":
                    api_post(f"/instances/{inst['id']}/stop", {})
                else:
                    _instance_id = inst["id"]
                    return _instance_id
    except Exception:
        pass

    # No running headed instance found — start a new one
    resp = api_post("/instances/start", {"profileId": "default", "mode": "headed"})
    if "error" in resp:
        raise RuntimeError(f"Failed to start PinchTab instance: {resp}")

    _instance_id = resp.get("id")
    
    # Wait up to 10 seconds for the instance to become ready
    import time
    for _ in range(10):
        status_resp = api_get(f"/instances/{_instance_id}")
        if status_resp.get("status") == "running":
            break
        time.sleep(1)

    return _instance_id


def get_tab_id() -> str:
    """Returns the current tab ID."""
    return _tab_id


def set_tab_id(tab_id: str):
    """Sets the current tab ID (called by open_browser_tab)."""
    global _tab_id
    _tab_id = tab_id
