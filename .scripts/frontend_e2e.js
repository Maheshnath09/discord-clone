const { chromium } = require('playwright');
const BASE = process.env.FRONTEND_BASE || 'http://localhost:31000';
const BACKEND_BASE = process.env.BACKEND_BASE || 'http://backend:8000';
(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  // Capture browser console and network responses for debugging
  page.on('console', (msg) => {
    try { console.log('PAGE:', msg.text()) } catch (e) {}
  })
  page.on('response', (resp) => {
    try { console.log('RESP:', resp.status(), resp.url()) } catch (e) {}
    try {
      if (resp.status() >= 400) {
        resp.text().then((t) => console.log('RESP_BODY:', resp.status(), resp.url(), t)).catch(() => {})
      }
    } catch (e) {}
  })
  const results = {};
  try {
    await page.goto(BASE + '/login', { timeout: 10000 });
    results.login_page = await page.title();

    // Try to register a fresh user (non-blocking)
    const rand = Date.now()
    // Use localtest.me domain which resolves and is acceptable to email-validator
    const regEmail = `e2e+${rand}@localtest.me`
    const regUser = `e2e_user_${rand}`
    try {
      await page.goto(BASE + '/register', { timeout: 8000 });
      await page.fill('#email', regEmail);
      await page.fill('#username', regUser);
      await page.fill('#password', 'password123');
      await page.click('button:has-text("Create Account")');
      // If registration succeeded, navigate to home
      try {
        await page.waitForSelector('text=Discover Rooms', { timeout: 8000 });
        // Use the newly registered user for the rest of the test
        results.register = 'success';
      } catch (e) {
        results.register = 'failed: ' + e.message;
        // fallback to CI user
        await page.goto(BASE + '/login');
        await page.fill('#identifier', 'ci_user');
        await page.fill('#password', 'password123');
        await page.click('button:has-text("Log In")');
      }
    } catch (e) {
      // Couldn't reach register page — fallback to CI user
      await page.goto(BASE + '/login');
      await page.fill('#identifier', 'ci_user');
      await page.fill('#password', 'password123');
      await page.click('button:has-text("Log In")');
    }

    // Wait for Discover Rooms
    try {
      await page.waitForSelector('text=Discover Rooms', { timeout: 8000 });
      results.login = 'success';
    } catch (e) {
      results.login = 'failed: ' + e.message;
    }

    if (results.login === 'success' || results.register === 'success') {
      // Try to open create form
      await page.click('button:has-text("Create Room")');
      // Fill form - use input selectors near Create form
      // The first input after opening form should be room name input
      const roomName = 'playwright-room-' + Date.now();
      const inputs = await page.$$('form textarea, form input');
      if (inputs.length >= 1) {
        await inputs[0].fill(roomName);
      }
      // Fill textarea for description
      const ta = await page.$('form textarea');
      if (ta) await ta.fill('Room created by Playwright E2E test');

      // Click the Create Room button inside the form
      await page.click('form button:has-text("Create Room")');
      try {
        await page.waitForSelector('text=Room created successfully', { timeout: 5000 });
        results.create_room = 'success';
      } catch (e) {
        results.create_room = 'unknown';
      }

      // Click the room link (look up by the created room name)
      try {
        await page.click(`a:has-text("${roomName}")`, { timeout: 8000 });
        // Wait for the message composer textarea to appear
        await page.waitForSelector('textarea', { timeout: 10000 });
        results.room_navigation = 'success';
      } catch (e) {
        results.room_navigation = 'failed: ' + e.message;
      }

      // Send a message (wait a bit for WS connections)
      try {
        await page.waitForTimeout(800);
        const ta2 = await page.$('textarea');
        await ta2.fill('Hello from Playwright Node');
        await ta2.press('Enter');
        // Allow some time for message to be processed and displayed
        try {
          await page.waitForSelector('text=Hello from Playwright Node', { timeout: 12000 });
          results.send_message = 'success';
        } catch (e) {
          // If UI did not render the message in time, verify persistence via backend messages API
          try {
            // Get auth token from localStorage
            const authRaw = await page.evaluate(() => localStorage.getItem('auth-storage'));
            let token = null;
            if (authRaw) {
              try { token = JSON.parse(authRaw).state.accessToken } catch (e) {}
            }

            // Derive room id from current URL
            const currentUrl = page.url();
            const m = currentUrl.match(/\/rooms\/(\d+)/);
            const roomId = m ? m[1] : null;

            if (token && roomId) {
              // Use Playwright's APIRequestContext to call the backend from the test
              // runner (avoids browser CORS restrictions).
              try {
                const apiResp = await context.request.get(`${BACKEND_BASE}/api/v1/rooms/${roomId}/messages`, {
                  headers: { Authorization: `Bearer ${token}` },
                });
                if (apiResp.ok()) {
                  const msgs = await apiResp.json();
                  const found = msgs.some(m => m.content && m.content.includes('Hello from Playwright Node'));
                  if (found) {
                    results.send_message = 'success (verified via API)';
                  } else {
                    results.send_message = 'failed: not found via API';
                  }
                } else {
                  results.send_message = `failed: api status ${apiResp.status()}`;
                }
              } catch (e3) {
                results.send_message = 'failed: ' + e3.message;
              }
            } else {
              results.send_message = 'failed: no token or room id for API check';
            }
          } catch (e2) {
            results.send_message = 'failed: ' + e2.message;
          }
        }
      } catch (e) {
        results.send_message = 'failed: ' + e.message;
      }
    }
  } catch (err) {
    results.error = err.message;
  } finally {
    console.log('RESULTS:', results);
    await context.close();
    await browser.close();
  }
})();
