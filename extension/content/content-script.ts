/** Standalone content script for Gmail - no imports allowed */

import { GmailDOMExtractor } from './content'

// Initialize the extractor
const extractor = new GmailDOMExtractor()

// Listen for messages from the popup
chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.action === 'runAgent') {
    try {
      // Extract email content
      const emailContent = extractor.extractEmailContent()
      
      // Send success response
      sendResponse({ success: true, emailContent })
    } catch (error) {
      console.error('Error running agent:', error)
      sendResponse({ success: false, error: error instanceof Error ? error.message : 'Unknown error' })
    }
    
    // Return true to indicate we'll send response asynchronously
    return true
  }
})

// Inject button when page loads
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    extractor.injectRunAgentButton()
  })
} else {
  extractor.injectRunAgentButton()
}
