# How to Check for Errors

## Step 1: Check Extension Errors
1. Go to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Look at "AI Execution Agent" card
4. If you see a red "Errors" button, click it
5. Copy and paste ALL errors you see

## Step 2: Check Console on Gmail
1. Open Gmail (mail.google.com)
2. Press F12 to open DevTools
3. Go to Console tab
4. Look for any red errors
5. Copy and paste them

## Step 3: Check Network Tab
1. In DevTools, go to Network tab
2. Click the extension icon
3. Click "Run Agent"
4. Look for any failed requests (red)
5. Tell me which file failed (404)

## Step 4: Verify Files Exist
Run these commands:
```powershell
cd D:\amd\extension
dir dist\content-script.js
dir ui\popup.html
dir ui\popup.js
dir content\content.css
```

Tell me if any file is missing.
