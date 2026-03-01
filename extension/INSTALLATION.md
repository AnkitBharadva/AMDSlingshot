# Chrome Extension Installation Guide

## Overview

This guide explains how to install and configure the AI Execution Agent Chrome Extension for Gmail.

## Prerequisites

- Google Chrome browser (version 88 or higher)
- Gmail account
- Backend API server running (see `backend/CONFIGURATION.md`)
- Node.js and npm (for building TypeScript)

## Building the Extension

### 1. Install Dependencies

```bash
# Navigate to extension directory
cd extension

# Install npm packages
npm install
```

Required packages:
- `typescript` - TypeScript compiler
- `@types/chrome` - Chrome API type definitions
- `fast-check` - Property-based testing library
- `jest` - Testing framework (if using Jest)

### 2. Compile TypeScript

```bash
# Compile TypeScript to JavaScript
npm run build
```

This will compile all `.ts` files to `.js` files in the same directory.

**Note**: If you don't have a build script, compile manually:
```bash
npx tsc
```

### 3. Verify Build Output

Ensure the following JavaScript files exist:
- `content/content.js`
- `api/api.js`
- `ui/ui.js`
- `actions/actions.js`
- `main.js`

## Loading the Extension in Chrome

### 1. Open Chrome Extensions Page

Choose one of these methods:
- Navigate to `chrome://extensions/` in the address bar
- Click the three-dot menu > "Extensions" > "Manage Extensions"
- Type `chrome://extensions` and press Enter

### 2. Enable Developer Mode

1. Look for the "Developer mode" toggle in the top-right corner
2. Click to enable it
3. Additional buttons will appear: "Load unpacked", "Pack extension", "Update"

### 3. Load Unpacked Extension

1. Click the "Load unpacked" button
2. Navigate to your `extension/` directory
3. Select the folder and click "Select Folder" (or "Open" on macOS)
4. The extension should now appear in your extensions list

### 4. Verify Installation

You should see:
- Extension name: "AI Execution Agent"
- Extension icon (if configured)
- Status: "Enabled"
- Extension ID (a long string of letters)

### 5. Pin Extension (Optional)

1. Click the puzzle piece icon in Chrome toolbar
2. Find "AI Execution Agent" in the list
3. Click the pin icon to keep it visible in the toolbar

## Configuring the Extension

### 1. Set Backend API Endpoint

The extension needs to know where your backend server is running.

**Option A: Edit Configuration File**

Create or edit `extension/config.js`:

```javascript
const CONFIG = {
  BACKEND_URL: 'http://localhost:8000',
  API_TIMEOUT_MS: 30000,
  CALENDAR_ID: 'primary'
};
```

**Option B: Use Extension Options Page** (if implemented)

1. Right-click the extension icon
2. Select "Options"
3. Enter backend URL: `http://localhost:8000`
4. Click "Save"

**Option C: Use Chrome Storage API** (if implemented)

The extension may prompt you for the backend URL on first use.

### 2. Configure CORS on Backend

Ensure your backend allows requests from the Chrome Extension:

In `backend/.env`:
```env
CORS_ORIGINS=chrome-extension://*
```

For production, use the specific extension ID:
```env
CORS_ORIGINS=chrome-extension://your-extension-id-here
```

To find your extension ID:
1. Go to `chrome://extensions/`
2. Find "AI Execution Agent"
3. Copy the ID shown below the extension name

## Using the Extension

### 1. Open Gmail

Navigate to https://mail.google.com/ and sign in.

### 2. Open an Email

Click on any email to view its contents.

### 3. Locate the "Run Agent" Button

The extension injects a "Run Agent" button into the Gmail interface. Look for it:
- Near the email subject line
- In the toolbar area
- Or in a custom panel (depending on implementation)

### 4. Click "Run Agent"

1. Click the "Run Agent" button
2. The extension will:
   - Extract email content
   - Send it to the backend API
   - Display a loading indicator
3. Wait for processing to complete (typically 5-15 seconds)

### 5. Review Results

After processing, you'll see:
- **Task Board**: Extracted tasks grouped by timeline (Today, Tomorrow, Upcoming)
- **Feedback Panel**: Statistics (tasks extracted, calendar blocks created, conflicts)
- **Execution Log**: Step-by-step processing details
- **Errors**: Any issues encountered (if applicable)

### 6. Interact with Tasks

For each task, you can:
- **Adjust Deadline**: Click the date picker to change the deadline
- **Discard Task**: Click the discard button to remove it
- **Export to CSV**: Click "Export CSV" to download all tasks
- **Export Meeting Prep**: Click "Export PDF" for meeting preparation documents

## Testing the Extension

### 1. Test with Sample Email

Create a test email in Gmail with actionable content:

```
Subject: Project Update - Deadline Tomorrow

Hi Team,

Please complete the following by tomorrow:
1. Review the Q4 report
2. Schedule a meeting with the client for next week
3. Update the project timeline

Thanks!
```

### 2. Click "Run Agent"

The extension should extract 3 tasks with appropriate deadlines and priorities.

### 3. Verify Calendar Integration

1. Open Google Calendar
2. Check for newly created calendar blocks
3. Verify block titles match task titles
4. Verify block times are within 30-60 minutes

### 4. Test Error Handling

Test with backend offline:
1. Stop the backend server
2. Click "Run Agent" in Gmail
3. Verify error message is displayed
4. Check that the extension doesn't crash

## Troubleshooting

### Issue: "Run Agent" button doesn't appear

**Solutions**:
1. Refresh the Gmail page (F5 or Ctrl+R)
2. Check that the extension is enabled in `chrome://extensions/`
3. Open browser console (F12) and check for JavaScript errors
4. Verify `manifest.json` has correct content script configuration
5. Try disabling and re-enabling the extension

### Issue: "Network error" or "Failed to fetch"

**Solutions**:
1. Verify backend server is running: `http://localhost:8000/docs`
2. Check backend URL in extension configuration
3. Verify CORS is configured correctly on backend
4. Check browser console for specific error messages
5. Ensure backend is accessible from your network

### Issue: Extension permissions error

**Solutions**:
1. Check `manifest.json` has required permissions:
   - `activeTab`
   - `storage`
   - Host permissions for Gmail (`https://mail.google.com/*`)
2. Reload the extension after changing permissions
3. Chrome may prompt for additional permissions - accept them

### Issue: Tasks not appearing after clicking "Run Agent"

**Solutions**:
1. Open browser console (F12) and check for errors
2. Verify backend returned a successful response (check Network tab)
3. Check that email content was extracted correctly
4. Verify UI rendering code is working (check console logs)
5. Try with a different email

### Issue: Calendar blocks not created

**Solutions**:
1. Verify Google Calendar API is configured on backend
2. Check backend logs for calendar API errors
3. Ensure OAuth token is valid (may need to re-authenticate)
4. Verify calendar ID is correct (usually "primary")
5. Check for scheduling conflicts in your calendar

### Issue: Extension crashes or becomes unresponsive

**Solutions**:
1. Open `chrome://extensions/`
2. Click "Errors" button on the extension
3. Review error details
4. Click "Reload" button to restart the extension
5. Check for infinite loops or memory leaks in code

### Issue: TypeScript compilation errors

**Solutions**:
1. Verify TypeScript is installed: `npm list typescript`
2. Check `tsconfig.json` configuration
3. Run `npm install` to ensure all dependencies are installed
4. Fix type errors in `.ts` files
5. Try `npm run build` again

## Development Tips

### Hot Reload During Development

Chrome extensions don't auto-reload when code changes. To reload:

1. Make code changes
2. Run `npm run build` to recompile TypeScript
3. Go to `chrome://extensions/`
4. Click the reload icon on your extension
5. Refresh Gmail page to test changes

**Tip**: Use a file watcher for automatic compilation:
```bash
npx tsc --watch
```

### Debugging

1. **Content Script Debugging**:
   - Open Gmail
   - Press F12 to open DevTools
   - Content script logs appear in the Console tab
   - Use `console.log()` for debugging

2. **Background Script Debugging** (if using service worker):
   - Go to `chrome://extensions/`
   - Click "service worker" link under your extension
   - A DevTools window opens for the background script

3. **Network Requests**:
   - Open DevTools (F12)
   - Go to Network tab
   - Filter by "Fetch/XHR"
   - Click "Run Agent" and watch API requests

### Testing

Run extension tests:
```bash
cd extension
npm test
```

Run specific test file:
```bash
npm test content.test.ts
```

## Updating the Extension

### After Code Changes

1. Make your code changes
2. Compile TypeScript: `npm run build`
3. Go to `chrome://extensions/`
4. Click reload icon on your extension
5. Refresh Gmail to test changes

### After Manifest Changes

If you modify `manifest.json`:
1. Go to `chrome://extensions/`
2. Click "Remove" on your extension
3. Click "Load unpacked" again
4. Select the extension folder

## Publishing to Chrome Web Store (Optional)

### 1. Prepare for Production

1. Update version in `manifest.json`
2. Create extension icons (16x16, 48x48, 128x128)
3. Test thoroughly in production mode
4. Remove debug code and console.logs
5. Update backend URL to production server

### 2. Create ZIP Package

```bash
cd extension
zip -r ai-execution-agent.zip . -x "*.ts" -x "node_modules/*" -x "*.test.js"
```

### 3. Submit to Chrome Web Store

1. Go to [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole/)
2. Pay one-time $5 developer fee (if first time)
3. Click "New Item"
4. Upload ZIP file
5. Fill in store listing details
6. Submit for review

## Security Considerations

1. **Permissions**: Only request necessary permissions in `manifest.json`
2. **HTTPS**: Always use HTTPS for backend API in production
3. **API Keys**: Never hardcode API keys in extension code
4. **Content Security Policy**: Follow CSP guidelines in manifest
5. **User Data**: Don't store sensitive email content locally

## Support

For issues or questions:
1. Check browser console for error messages
2. Review this installation guide
3. Check backend configuration guide
4. Consult Chrome Extension documentation: https://developer.chrome.com/docs/extensions/
5. Review manifest V3 migration guide if needed

## Uninstalling

To remove the extension:
1. Go to `chrome://extensions/`
2. Find "AI Execution Agent"
3. Click "Remove"
4. Confirm removal

Your Gmail will return to normal without the "Run Agent" button.
