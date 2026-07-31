"""
Local Outlook Email Agent for Synapse OS
========================================

This script must be run NATIVELY on Windows (not inside Docker).
It uses the local COM interface to read emails from the desktop Outlook client
and pushes them securely to your local Synapse OS backend for vector ingestion.

Prerequisites:
- Windows OS
- Microsoft Outlook installed and configured
- Python installed on your host machine
- Run: pip install pywin32 requests

Usage:
    python local_outlook_agent.py
"""

import sys
import time
import requests
import datetime
try:
    import win32com.client
except ImportError:
    print("ERROR: pywin32 is not installed.")
    print("Please install it by running: pip install pywin32")
    sys.exit(1)

# Configuration
SYNAPSE_API_URL = "http://localhost:8000/documents/"
MAX_EMAILS = 10 # Number of recent emails to sync

def sync_recent_emails():
    print(f"Connecting to Local Outlook Application...")
    try:
        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    except Exception as e:
        print(f"Failed to connect to Outlook. Is it installed and running? Error: {e}")
        return

    # 6 refers to the Inbox folder
    inbox = outlook.GetDefaultFolder(6)
    messages = inbox.Items
    
    # Sort messages by ReceivedTime in descending order
    messages.Sort("[ReceivedTime]", True)

    print(f"Connected! Syncing the {MAX_EMAILS} most recent emails...")
    
    success_count = 0
    for i, message in enumerate(messages):
        if i >= MAX_EMAILS:
            break
            
        try:
            subject = message.Subject
            body = message.Body
            sender = message.SenderEmailAddress
            received_time = message.ReceivedTime
            
            # Construct the content string
            content = f"From: {sender}\nReceived: {received_time}\n\n{body}"
            
            # Prepare payload for Synapse OS
            payload = {
                "title": f"Email: {subject}",
                "source_type": "email",
                "content": content,
                "source_url": None
            }
            
            print(f"[{i+1}/{MAX_EMAILS}] Pushing: {subject[:40]}...")
            
            # Post to Synapse Backend
            response = requests.post(SYNAPSE_API_URL, json=payload)
            response.raise_for_status()
            success_count += 1
            
        except Exception as e:
            print(f"  -> Failed to process email: {e}")

    print("-" * 40)
    print(f"Done! Successfully synced {success_count} emails to Synapse OS.")

if __name__ == "__main__":
    sync_recent_emails()
