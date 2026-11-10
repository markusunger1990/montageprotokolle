#!/usr/bin/env python3
"""Verschickt ein Protokoll-PDF per AgentMail-API (API-Key wird vom Proxy injiziert).
Aufruf: python3 send.py protokolle/<datei>.pdf "Betreff" "Text" """
import sys, os, json, base64, urllib.request
INBOX = "markus-flynn@agentmail.to"
TO = "markusunger1990@icloud.com"
pdf, subject, text = sys.argv[1], sys.argv[2], sys.argv[3]
body = {"to": [TO], "subject": subject, "text": text,
        "attachments": [{"filename": os.path.basename(pdf), "content_type": "application/pdf",
                         "content": base64.b64encode(open(pdf, "rb").read()).decode()}]}
req = urllib.request.Request(f"https://api.agentmail.to/v0/inboxes/{INBOX}/messages/send",
    data=json.dumps(body).encode(), method="POST",
    headers={"Content-Type": "application/json", "Authorization": "Bearer proxy-injected"})
try:
    with urllib.request.urlopen(req) as r: print("OK", r.status, r.read().decode()[:200])
except urllib.error.HTTPError as e:
    print("FEHLER", e.code, e.read().decode()[:500]); sys.exit(1)
