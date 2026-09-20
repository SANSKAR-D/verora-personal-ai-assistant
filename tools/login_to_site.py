import os
import time
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

# Global variables to keep the browser open!
_p = None
_browser = None

def get_browser():
    global _p, _browser
    if _p is None:
        _p = sync_playwright().start()
    if _browser is None or not _browser.is_connected():
        _browser = _p.chromium.launch(headless=False, slow_mo=50)
    return _browser

def login_to_site(login_url: str, site_name: str) -> str:
    """
    Logs into ANY website by automatically finding the username/password boxes!
    Example: login_to_site("https://github.com/login", "GITHUB")
    """
    
    env_var_user = f"{site_name.upper()}_USERNAME"
    env_var_pass = f"{site_name.upper()}_PASSWORD"
    
    username = os.getenv(env_var_user)
    password = os.getenv(env_var_pass)
    
    if not username or not password:
        return f"No stored credentials for {site_name} in .env file (looked for {env_var_user} and {env_var_pass})"

    try:
        browser = get_browser()
        page = browser.new_page()
            
        # Go to the requested login URL
        page.goto(login_url)
        
        # 1. Smart Search for Username Box
        # Looks for any input box meant for emails, usernames, or logins
        username_box = page.locator("input[type='email'], input[name*='user'], input[name*='email'], input[name*='login'], input[id*='user'], input[id*='email'], input[id*='login'], input[type='text']").first
        try:
            username_box.fill(username, timeout=5000)
        except:
            return "Could not find the username box within 5 seconds! The site might be loading too slowly or uses a non-standard login form."
            
        # 2. Smart Search for Password Box
        password_box = page.locator("input[type='password']").first
        try:
            password_box.fill(password, timeout=5000)
        except:
            return "Could not automatically find the password box."
            
        # 3. Smart Search for Login Button
        submit_button = page.locator("button[type='submit'], input[type='submit'], button:has-text('Log in'), button:has-text('Sign in'), button:has-text('Login')").first
        try:
            submit_button.click(timeout=3000)
        except:
            # If it can't find the button, just press Enter on the password!
            password_box.press("Enter")
            
        # We no longer close the browser! It stays open for you!
        return f"Successfully opened browser and attempted login for {site_name}!"
                
    except Exception as e:
        return f"Failed to log in using Playwright: {e}"
