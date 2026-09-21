import os
from dotenv import load_dotenv
from agent.confirmation import confirm_action
from tools.pinchtab_manager import get_instance_id, set_tab_id, api_post, api_get

load_dotenv()

def get_credentials(site_name: str):
    """Pulls username/password from environment variables, e.g. GITHUB_USERNAME / GITHUB_PASSWORD."""
    prefix = site_name.upper()
    username = os.environ.get(f"{prefix}_USERNAME")
    password = os.environ.get(f"{prefix}_PASSWORD")
    return username, password


def login_to_site(login_url: str, site_name: str) -> str:
    """Logs into ANY website using credentials stored securely in environment variables.
    It automatically discovers the username and password fields using PinchTab snapshots.

    Use this when the user asks to log into, sign into, or authenticate with a specific site.

    This action requires explicit user confirmation before it executes.

    Args:
        login_url: The direct URL to the site's login page (e.g. 'https://github.com/login').
        site_name: The name of the site (used to find credentials in .env, e.g. 'github').

    Returns:
        A message confirming the login attempt, or an error if credentials are missing.
    """
    username, password = get_credentials(site_name)
    if not username or not password:
        return f"No credentials found in .env for {site_name} (expected {site_name.upper()}_USERNAME / {site_name.upper()}_PASSWORD)"

    if not confirm_action(f"Log into {site_name} at {login_url} as {username}?"):
        return "Login cancelled by user."

    try:
        instance_id = get_instance_id()

        # Open the login page
        resp = api_post(
            f"/instances/{instance_id}/tabs/open",
            {"url": login_url},
        )
        tab_id = resp.get("tabId") or resp.get("id")
        if not tab_id:
            return f"Failed to open login page. Response: {resp}"

        set_tab_id(tab_id)

        # Use snapshot to auto-discover fields
        # Note: PinchTab API returns {"count": N, "nodes": [...]}
        snapshot_data = api_get(f"/tabs/{tab_id}/snapshot", params={"filter": "interactive"})
        
        nodes = []
        if isinstance(snapshot_data, dict) and "nodes" in snapshot_data:
            nodes = snapshot_data["nodes"]
        elif isinstance(snapshot_data, list):
            nodes = snapshot_data

        if nodes:
            username_ref = None
            password_ref = None
            submit_ref = None

            for elem in nodes:
                role = elem.get("role", "").lower()
                name = (elem.get("name", "") or elem.get("text", "")).lower()
                ref = elem.get("ref", "")

                if role in ["textbox", "searchbox", "email"] and not username_ref:
                    if any(kw in name for kw in ["user", "email", "login", "username"]):
                        username_ref = ref
                    elif not username_ref:
                        username_ref = ref  # First textbox as fallback

                if role == "textbox" and "password" in name:
                    password_ref = ref

                if role == "button" and any(kw in name for kw in ["sign in", "log in", "login", "submit", "continue"]):
                    submit_ref = ref

            if username_ref:
                api_post(f"/tabs/{tab_id}/action", {"kind": "fill", "ref": username_ref, "value": username})
            else:
                return "Could not find username field on the login page."

            if password_ref:
                api_post(f"/tabs/{tab_id}/action", {"kind": "fill", "ref": password_ref, "value": password})
            else:
                return "Could not find password field on the login page."

            if submit_ref:
                api_post(f"/tabs/{tab_id}/action", {"kind": "click", "ref": submit_ref})
            else:
                # Fallback: press Enter on the password field
                api_post(f"/tabs/{tab_id}/action", {"kind": "press", "ref": password_ref, "key": "Enter"})

            return f"Login attempt to {site_name} completed using auto-discovered refs."

        return f"Could not read login page snapshot. Response: {snapshot_data}"

    except Exception as e:
        return f"Failed to log in: {e}"
