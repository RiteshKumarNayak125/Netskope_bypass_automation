import json
import time
from datetime import datetime
import os
import sys 

# ====================================================================
# PROJECT SUMMARY: TIMED NETSKOPE BYPASS AUTOMATION (SOAR PLAYBOOK)
# ====================================================================
# This script simulates a Security Orchestration, Automation, and Response (SOAR)
# playbook that runs upon receiving an "Approved" webhook from Jira.
#
# OBJECTIVE: To temporarily disable Netskope protection for a user (via group removal)
# for a specific duration, but only if their security risk score is acceptable.
#
# REAL-WORLD COMPONENTS SIMULATED:
# 1. Trigger: Jira Webhook (Input: mock_jira_webhook.json)
# 2. Enrichment: Netskope Risk Exchange / SIEM Lookup (Input: mock_user_history.json)
# 3. Enforcement: Netskope API (Output: mock_netskope_db.txt)
# 4. Email Notification: (Mocked function below)
# 5. Scheduling: Time-based revocation (time.sleep)

# --------------------------------------------------------------------
# CONFIGURATION
# --------------------------------------------------------------------
MOCK_DB_FILE = "/app/mock_netskope_db.txt"
MOCK_HISTORY_FILE = "/app/mock_user_history.json"
RISK_SCORE_THRESHOLD = 70 # Policy blocks if risk score is >= 70

# --- MOCK & UTILITY FUNCTIONS ---

def draw_loading_bar(text, duration=2):
    """Draws a simple ASCII loading animation with custom text."""
    symbols = ['-', '\\', '|', '/']
    print(f"\n****** {text} ******")
    for i in range(duration * 4): # 4 steps per second
        sys.stdout.write(f"\r* Processing {symbols[i % 4]} *")
        sys.stdout.flush()
        time.sleep(0.25)
    print("\r* Finished! *")


def send_email_notification(recipient, subject, body):
    """
    MOCK FUNCTION: Simulates sending a completion email to the user.
    """
    print(f"\n[EMAIL MOCK] Sending Notification to: {recipient}")
    print(f"  Subject: {subject}")
    print(f"  Body Snippet: {body[:60]}...")
    print("[EMAIL MOCK] Email job completed.")


def get_user_enrichment(user_email):
    """Simulates API call to Netskope Risk Exchange or SIEM for user history."""
    try:
        with open(MOCK_HISTORY_FILE, 'r') as f:
            content = f.read().strip()
            if not content:
                 print("[INFO] Mock history file is empty. Using default score 0.")
                 return {}
            data = json.loads(content)
            return data.get(user_email, {}) 
    except Exception as e:
        print(f"[ERROR] Could not load user history (JSON Error: {e}). Using default score 0.")
        return {}


def netskope_api_add_user(user_email):
    """Simulates Netskope API call to add user to the bypass group."""
    print(f"\n[NETSKOPE MOCK API] Sending API call to ADD user: {user_email}")
    try:
        with open(MOCK_DB_FILE, "a+") as f:
            f.seek(0)
            existing_users = {line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')}
            
            if user_email not in existing_users:
                f.write(f"{user_email}\n")
                print(f"  --> SUCCESS: {user_email} added to {MOCK_DB_FILE}")
        return True
    except Exception:
        return False

def netskope_api_remove_user(user_email):
    """Simulates Netskope API call to remove user from the bypass group."""
    print(f"\n[NETSKOPE MOCK API] Sending API call to REMOVE user: {user_email}")
    try:
        with open(MOCK_DB_FILE, "r") as f:
            lines = f.readlines()
        
        updated_lines = [line for line in lines if line.strip() != user_email]
        
        with open(MOCK_DB_FILE, "w") as f:
            f.writelines(updated_lines)
        
        print(f"  --> SUCCESS: {user_email} removed from {MOCK_DB_FILE}")
        return True
    except Exception:
        return False

# --------------------------------------------------------------------
# MAIN PLAYBOOK ORCHESTRATION
# --------------------------------------------------------------------
def handle_jira_webhook(webhook_payload_path):
    """Orchestrates the policy enforcement based on Jira input and security context."""
    print("\n" + "="*70)
    print(f"Starting SOAR Playbook Execution - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # --- JIRA PAYLOAD PARSING ---
    try:
        with open(webhook_payload_path, 'r') as f:
            data = json.load(f)
    except Exception:
        print("[CRITICAL ERROR] Failed to load JSON payload.")
        sys.exit(1)

    try:
        jira_key = data['issue']['key']
        user_email = data['issue']['fields']['customfield_10010']['emailAddress']
        duration_hours = data['issue']['fields']['customfield_10011']
        user_display_name = data['issue']['fields']['customfield_10010']['displayName']
    except Exception:
        print("[CRITICAL ERROR] Missing required Jira fields (Ticket/User/Duration).")
        sys.exit(1)

    # --- ACTION SUMMARY (Required for SOAR Output) ---
    print("\n--- INITIATION & CONTEXT ---")
    print(f"  TICKET NUMBER: {jira_key}")
    print(f"  USER NAME: {user_display_name}")
    print(f"  USER EMAIL: {user_email}")
    print(f"  REQUESTED DURATION: {duration_hours} hours")
    
    
    # --- POLICY ENRICHMENT ---
    draw_loading_bar("POLICY ENRICHMENT: Fetching User Risk Profile", duration=2)
    user_context = get_user_enrichment(user_email)
    
    current_risk = user_context.get("current_risk_score", 0)
    last_bypass = user_context.get("last_bypass_date", "N/A")
    last_event = user_context.get("last_event", "N/A")

    print(f"\n  -> Netskope Current Risk Score: {current_risk}")
    print(f"  -> Last Bypass Date: {last_bypass}")
    print(f"  -> Last Risky Event: {last_event}")

    
    # --- CONDITIONAL POLICY CHECK ---
    draw_loading_bar("CONTAINMENT CHECK: Evaluating Risk Threshold", duration=1)
    
    if current_risk >= RISK_SCORE_THRESHOLD:
        denial_reason = f"Automated Denial: Current Risk Score ({current_risk}) is >= Threshold ({RISK_SCORE_THRESHOLD})."
        print(f"\n  -> [POLICY BLOCKED]: {denial_reason}")
        print(f"[JIRA MOCK API] Updating ticket {jira_key} to status 'Denied'.")
        send_email_notification(user_email, f"Jira {jira_key} Denied: High Risk Score", denial_reason)
        print("="*70)
        return
        
    print(f"\n  -> [POLICY ALLOWED]: Risk Score ({current_risk}) is acceptable. Proceeding to enforcement.")


    # --- ENFORCEMENT ACTION (ADD) ---
    print("\n--- ENFORCEMENT ACTION: Enabling Netskope Bypass ---")
    if netskope_api_add_user(user_email):
        print(f"[SUCCESS] {user_email}'s Netskope access is now bypassed.")
        print(f"[JIRA MOCK API] Updating ticket {jira_key} status to 'In Progress'.")
        send_email_notification(user_email, f"Jira {jira_key} Approved: Bypass Enabled", f"Your Netskope bypass is enabled for {duration_hours} hours.")
    else:
        print("[CRITICAL ERROR] Failed to enable bypass. Aborting.")
        sys.exit(1)


    # --- TIMED REVOCATION SCHEDULING ---
    print("\n--- TIMED REVOCATION SCHEDULING ---")
    wait_seconds = 10 # 10 seconds for demo
    
    print(f"[SCHEDULER MOCK] Pausing container for {wait_seconds} seconds (Simulated {duration_hours} hours).")
    time.sleep(wait_seconds) 
    
    print("\n--- REVOCATION EXECUTION ---")
    if netskope_api_remove_user(user_email):
        print(f"[SUCCESS] {user_email}'s Netskope protection has been restored.")
        send_email_notification(user_email, f"Jira {jira_key} Complete: Bypass Revoked", "Your temporary Netskope bypass has been automatically revoked.")
    else:
        print("[ERROR] Failed to disable bypass. Manual investigation required!")

    # --- FINAL TICKET UPDATE ---
    print("\n--- FINAL TICKET UPDATE ---")
    print(f"[JIRA MOCK API] Resolving ticket {jira_key} with final details.")
    print("="*70)


# --- EXECUTION START ---
if __name__ == "__main__":
    if not os.path.exists(MOCK_HISTORY_FILE):
        print(f"[CRITICAL ERROR] Missing required file: {MOCK_HISTORY_FILE}")
        sys.exit(1)
        
    handle_jira_webhook("/app/mock_jira_webhook.json")
