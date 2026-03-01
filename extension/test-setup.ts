/** Test setup for Vitest. */

import { afterEach } from 'vitest'

// Cleanup after each test
afterEach(() => {
  // Clean up DOM
  if (typeof document !== 'undefined') {
    document.body.innerHTML = ''
  }
})
