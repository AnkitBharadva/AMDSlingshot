/** Popup UI script for the Chrome Extension. */

// Load saved settings when popup opens
document.addEventListener('DOMContentLoaded', async () => {
  const settings = await chrome.storage.local.get(['backendUrl', 'calendarId', 'timezone'])
  
  if (settings.backendUrl) {
    document.getElementById('backendUrl').value = settings.backendUrl
  }
  if (settings.calendarId) {
    document.getElementById('calendarId').value = settings.calendarId
  }
  if (settings.timezone) {
    document.getElementById('timezone').value = settings.timezone
  }
})

// Save settings
document.getElementById('saveSettings').addEventListener('click', async () => {
  const backendUrl = document.getElementById('backendUrl').value.trim()
  const calendarId = document.getElementById('calendarId').value.trim()
  const timezone = document.getElementById('timezone').value.trim()
  
  if (!backendUrl || !calendarId || !timezone) {
    showStatus('Please fill in all fields', 'error')
    return
  }
  
  await chrome.storage.local.set({
    backendUrl,
    calendarId,
    timezone
  })
  
  showStatus('Settings saved successfully!', 'success')
})

// Run agent
document.getElementById('runAgent').addEventListener('click', async () => {
  // Check if settings are configured
  const settings = await chrome.storage.local.get(['backendUrl', 'calendarId', 'timezone'])
  
  if (!settings.backendUrl || !settings.calendarId || !settings.timezone) {
    showStatus('Please configure settings first', 'error')
    return
  }
  
  // Get the active tab
  const tabs = await chrome.tabs.query({ active: true, currentWindow: true })
  const activeTab = tabs[0]
  
  // Check if we're on Gmail
  if (!activeTab.url.includes('mail.google.com')) {
    showStatus('Please open Gmail to use this extension', 'error')
    return
  }
  
  showStatus('Extracting email content...', 'success')
  
  // Send message to content script to extract email
  chrome.tabs.sendMessage(activeTab.id, { action: 'runAgent' }, async (response) => {
    if (chrome.runtime.lastError) {
      showStatus('Error: ' + chrome.runtime.lastError.message, 'error')
      return
    }
    
    if (!response || !response.success) {
      showStatus('Failed to extract email: ' + (response?.error || 'Unknown error'), 'error')
      return
    }
    
    // Email extracted successfully, now send to backend
    showStatus('Sending to backend...', 'success')
    
    try {
      const backendResponse = await fetch(`${settings.backendUrl}/run-agent`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email_content: response.emailContent,
          user_timezone: settings.timezone,
          calendar_id: settings.calendarId
        })
      })
      
      if (!backendResponse.ok) {
        throw new Error(`Backend returned ${backendResponse.status}: ${backendResponse.statusText}`)
      }
      
      const result = await backendResponse.json()
      
      // Show results
      if (result.errors && result.errors.length > 0) {
        showStatus(`Completed with errors: ${result.errors[0].message}`, 'error')
      } else {
        showStatus(`Success! Extracted ${result.stats.tasks_extracted} tasks, created ${result.stats.calendar_blocks_created} calendar blocks`, 'success')
      }
      
      console.log('Backend response:', result)
    } catch (error) {
      showStatus('Backend error: ' + error.message, 'error')
      console.error('Backend error:', error)
    }
  })
})

function showStatus(message, type) {
  const statusEl = document.getElementById('status')
  statusEl.textContent = message
  statusEl.className = 'status ' + type
  
  // Auto-hide success messages after 5 seconds
  if (type === 'success') {
    setTimeout(() => {
      statusEl.className = 'status'
    }, 5000)
  }
}

