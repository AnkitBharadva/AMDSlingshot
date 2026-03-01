# Quick Fix for "Receiving end does not exist"

This error means the content script isn't loaded on the Gmail page.

## Fix Steps:

### 1. Rebuild Extension
```powershell
cd D:\amd\extension
npm run build
```

### 2. Completely Remove and Reinstall Extension
**IMPORTANT: Don't just reload - REMOVE it completely**

1. Go to `chrome://extensions/`
2. Find "AI Execution Agent"
3. Click **REMOVE** button (trash icon)
4. Click **Load unpacked** button
5. Select folder: `D:\amd\extension`

### 3. Close ALL Gmail Tabs
- Close every tab with `mail.google.com`
- Don't just refresh - CLOSE them

### 4. Open Fresh Gmail Tab
1. Open a **NEW** tab (Ctrl+T)
2. Go to https://mail.google.com
3. Open an email

### 5. Check if Content Script Loaded
1. Press F12 on Gmail page
2. Go to Console tab
3. Type: `document.querySelector('.ai-execution-agent-button')`
4. Press Enter
5. If it returns `null`, content script didn't load
6. If it returns an element, content script loaded successfully

### 6. Test Extension
1. Click extension icon in Chrome toolbar
2. Click "Run Agent"

## If Still Not Working

Check Console on Gmail page (F12 → Console) for errors like:
- "Unexpected token 'export'"
- "Cannot use import statement"
- Any red errors

Tell me what error you see.
