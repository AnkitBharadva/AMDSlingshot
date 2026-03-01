import { describe, it, expect } from 'vitest'
import { readFileSync } from 'fs'
import { join } from 'path'

describe('Manifest V3 Validation', () => {
  let manifest: any

  // Load manifest.json before tests
  try {
    const manifestPath = join(__dirname, 'manifest.json')
    const manifestContent = readFileSync(manifestPath, 'utf-8')
    manifest = JSON.parse(manifestContent)
  } catch (error) {
    console.error('Failed to load manifest.json:', error)
  }

  it('should be valid Manifest V3 format', () => {
    expect(manifest).toBeDefined()
    expect(manifest.manifest_version).toBe(3)
  })

  it('should have required metadata fields', () => {
    expect(manifest.name).toBeDefined()
    expect(manifest.name).toBe('AI Execution Agent')
    
    expect(manifest.version).toBeDefined()
    expect(manifest.version).toMatch(/^\d+\.\d+\.\d+$/) // Semantic versioning
    
    expect(manifest.description).toBeDefined()
    expect(manifest.description.length).toBeGreaterThan(0)
  })

  it('should declare required permissions', () => {
    expect(manifest.permissions).toBeDefined()
    expect(Array.isArray(manifest.permissions)).toBe(true)
    
    // Check for activeTab permission
    expect(manifest.permissions).toContain('activeTab')
    
    // Check for storage permission
    expect(manifest.permissions).toContain('storage')
  })

  it('should declare host permissions for Gmail', () => {
    expect(manifest.host_permissions).toBeDefined()
    expect(Array.isArray(manifest.host_permissions)).toBe(true)
    
    // Check for Gmail host permissions
    expect(manifest.host_permissions).toContain('https://www.gmail.com/*')
    expect(manifest.host_permissions).toContain('https://mail.google.com/*')
  })

  it('should configure service worker correctly', () => {
    expect(manifest.background).toBeDefined()
    expect(manifest.background.service_worker).toBeDefined()
    expect(manifest.background.service_worker).toBe('background/service-worker.js')
  })

  it('should configure content scripts for Gmail', () => {
    expect(manifest.content_scripts).toBeDefined()
    expect(Array.isArray(manifest.content_scripts)).toBe(true)
    expect(manifest.content_scripts.length).toBeGreaterThan(0)
    
    const gmailContentScript = manifest.content_scripts[0]
    
    // Check matches for Gmail URLs
    expect(gmailContentScript.matches).toBeDefined()
    expect(gmailContentScript.matches).toContain('https://www.gmail.com/*')
    expect(gmailContentScript.matches).toContain('https://mail.google.com/*')
    
    // Check that JS files are specified
    expect(gmailContentScript.js).toBeDefined()
    expect(Array.isArray(gmailContentScript.js)).toBe(true)
    expect(gmailContentScript.js.length).toBeGreaterThan(0)
  })

  it('should have icon configuration', () => {
    expect(manifest.icons).toBeDefined()
    
    // Check for standard icon sizes
    expect(manifest.icons['16']).toBeDefined()
    expect(manifest.icons['48']).toBeDefined()
    expect(manifest.icons['128']).toBeDefined()
  })

  it('should not use deprecated Manifest V2 features', () => {
    // Ensure no background.page or background.scripts (V2 features)
    if (manifest.background) {
      expect(manifest.background.page).toBeUndefined()
      expect(manifest.background.scripts).toBeUndefined()
    }
    
    // Ensure no browser_action (V2 feature, replaced by action in V3)
    expect(manifest.browser_action).toBeUndefined()
  })

  it('should have valid action configuration', () => {
    expect(manifest.action).toBeDefined()
    expect(manifest.action.default_title).toBeDefined()
  })
})
