# Troubleshooting Guide

## "Receiving end does not exist" Error

This error means the content script isn't loaded on the Gmail page.

### Solution:

1. **Rebuild the extension:**
   ```powershell
   cd D:\amd\extension
   npm run build
   ```

2. **Completely remove and reload the extension:**
   - Go to `chrome://extensions/`
   - Find "AI Execution Agent"
   - Click **Remove** (not just the reload icon)
   - Click **Load unpacked**
   - Select `D:\amd\extension` folder

3. **Close ALL Gmail tabs and open a fresh one:**
   - Close all tabs with `mail.google.com`
   - Open a NEW tab
   - Navigate to https://mail.google.com
   - Open your test email

4. **Test the extension:**
   - Click the extension icon in Chrome toolbar
   - Click "Run Agent"

## 404 Not Found Error

This means a file referenced in manifest.json doesn't exist.

### Check these files exist:

- `extension/dist/content-script.js` (bundled by webpack)
- `extension/background/service-worker.js`
- `extension/content/content.css`
- `extension/ui/popup.html`
- `extension/ui/popup.js`

### To verify files exist:
```powershell
cd D:\amd\extension
dir dist\content-script.js
dir background\service-worker.js
dir content\content.css
dir ui\popup.html
dir ui\popup.js
```

### If content-script.js is missing:
```powershell
cd D:\amd\extension
npm run build
```

This should create `dist/content-script.js`.

## Check Chrome DevTools for Specific 404

1. Go to `chrome://extensions/`
2. Find "AI Execution Agent"
3. Click "Inspect views: service worker" or "Errors"
4. Look at the Console tab
5. Find the 404 error - it will show the exact file path that's missing

## Backend Connection Issues

If you get "Failed to fetch" or connection errors:

1. **Verify backend is running:**
   ```powershell
   cd D:\amd\backend
   # Activate virtual environment
   amd\Scripts\activate
   # Start server
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Check backend URL in extension settings:**
   - Should be: `http://localhost:8000` (no trailing slash)

3. **Verify CORS is configured:**
   - Backend `.env` should have: `CORS_ORIGINS=chrome-extension://*`

## Content Script Not Injecting

If the content script loads but doesn't work:

1. **Check the Console in Gmail tab:**
   - Open Gmail
   - Press F12 to open DevTools
   - Go to Console tab
   - Look for errors related to "AI Execution Agent"

2. **Verify content script is injected:**
   - In DevTools Console, type: `document.querySelector('.ai-execution-agent-button')`
   - Should return an element (the button)
   - If null, content script didn't inject

3. **Check manifest.json matches:**
   - Content scripts should match: `["https://www.gmail.com/*", "https://mail.google.com/*"]`
   - Content script JS should be: `["dist/content-script.js"]`

## Still Having Issues?

1. Check the exact error message in Chrome DevTools Console
2. Check the Network tab in DevTools to see which requests are failing
3. Verify all files exist in the extension directory
4. Try restarting Chrome completely
