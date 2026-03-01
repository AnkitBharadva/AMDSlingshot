# AI Execution Agent Chrome Extension

Chrome Extension for extracting actionable tasks from Gmail emails and scheduling them on Google Calendar.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Build the extension:
```bash
npm run build
```

3. Load the extension in Chrome:
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select the `extension` directory

4. Run tests:
```bash
npm test
```

## Development

```bash
# Watch mode for development
npm run test:watch
```

## Manifest V3 Compliance

This extension follows Chrome's Manifest V3 specification with:
- Service workers instead of background pages
- Minimal permissions
- HTTPS-only communication
