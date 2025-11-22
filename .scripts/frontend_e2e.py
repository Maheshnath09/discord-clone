from playwright.sync_api import sync_playwright
import time, os

BASE = os.environ.get('FRONTEND_BASE', 'http://localhost:31000')
CI_USER = {'username': 'ci_user', 'password': 'password123'}

results = {}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Open login page
    page.goto(f"{BASE}/login", timeout=10000)
    results['login_page'] = page.title()

    # Fill login form
    page.fill('#identifier', CI_USER['username'])
    page.fill('#password', CI_USER['password'])
    page.click('button:has-text("Log In")')

    # Wait for navigation to rooms page (Discover Rooms)
    try:
        page.wait_for_selector('text=Discover Rooms', timeout=8000)
        results['login'] = 'success'
    except Exception as e:
        results['login'] = f'failed: {e}'

    # Create a room via UI
    if results.get('login') == 'success':
        # Click Create Room
        page.click('button:has-text("Create Room")')
        # Fill form fields
        page.fill('input[placeholder="Room name"]', 'playwright-room') if False else None
        # The create form uses inputs without placeholders; use label text selectors
        page.fill('input:nth-of-type(1)', 'playwright-room')
        # Fill description textarea (there's only one textarea in create form)
        page.fill('textarea', 'Room created by Playwright E2E test')
        # Click Create Room button in form
        page.click('button:has-text("Create Room")')

        # Wait for success message
        try:
            page.wait_for_selector('text=Room created successfully', timeout=5000)
            results['create_room'] = 'success'
        except Exception:
            # Maybe room exists already; check for link
            results['create_room'] = 'unknown'

        # Find the created room in the list and navigate
        try:
            # Room link by text
            page.click('a:has-text("playwright-room")')
            page.wait_for_selector('text=Type a message...', timeout=5000)
            results['room_navigation'] = 'success'
        except Exception as e:
            results['room_navigation'] = f'failed: {e}'

        # Send a message via composer
        try:
            textarea = page.query_selector('textarea')
            textarea.fill('Hello from Playwright')
            # Press Enter to send (since Enter without shift sends)
            textarea.press('Enter')
            # Wait for message to appear in chat
            page.wait_for_selector('text=Hello from Playwright', timeout=5000)
            results['send_message'] = 'success'
        except Exception as e:
            results['send_message'] = f'failed: {e}'

    # Close
    context.close()
    browser.close()

print(results)
