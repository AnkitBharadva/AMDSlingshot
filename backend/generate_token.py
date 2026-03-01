"""
Google Calendar API Token Generator

This script generates the token.json file needed for Google Calendar API authentication.
Run this script once to authenticate and generate the token.
"""

import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these scopes, delete the token.json file.
SCOPES = [
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/calendar.readonly'
]

def generate_token():
    """Generate token.json through OAuth2 flow."""
    
    # Paths
    credentials_path = 'credentials.json'
    token_path = 'token.json'
    
    # Check if credentials.json exists
    if not os.path.exists(credentials_path):
        print(f"❌ Error: {credentials_path} not found!")
        print("\nPlease download your OAuth2 credentials from Google Cloud Console:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Navigate to 'APIs & Services' > 'Credentials'")
        print("3. Download the OAuth2 client credentials")
        print(f"4. Save as '{credentials_path}' in the backend directory")
        return
    
    creds = None
    
    # Check if token.json already exists
    if os.path.exists(token_path):
        print(f"⚠️  {token_path} already exists!")
        response = input("Do you want to regenerate it? (y/n): ")
        if response.lower() != 'y':
            print("Aborted. Using existing token.")
            return
        
        print("Deleting existing token...")
        os.remove(token_path)
    
    # The file token.json stores the user's access and refresh tokens
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("\n🔐 Starting OAuth2 authentication flow...")
            print("A browser window will open for you to sign in with Google.")
            print("Please grant the requested calendar permissions.\n")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)
            
            # Run the OAuth flow
            # This will open a browser window
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        
        print(f"\n✅ Success! {token_path} has been generated.")
        print(f"📁 Location: {os.path.abspath(token_path)}")
        print("\n⚠️  Important: Never commit token.json to version control!")
        print("Add it to .gitignore to keep your credentials secure.")
    else:
        print("✅ Valid credentials already exist.")

if __name__ == '__main__':
    print("=" * 60)
    print("Google Calendar API Token Generator")
    print("=" * 60)
    print()
    
    try:
        generate_token()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure credentials.json is valid")
        print("2. Check that Google Calendar API is enabled in your project")
        print("3. Verify OAuth consent screen is configured")
        print("4. Make sure your email is added as a test user")
        print("5. Check your internet connection")
