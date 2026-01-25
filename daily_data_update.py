import subprocess
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import pandas as pd

# Email settings
SENDER_EMAIL = 'joey19154@gmail.com'
SENDER_PASSWORD = 'qchyceomnnqujkkr'
RECIPIENT_EMAIL = 'joey19154@gmail.com'

print(f"\n{'='*70}")
print(f"NBA Data Daily Update - {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
print(f"{'='*70}\n")

# Run get_nba_data.py
print("[1/2] Fetching latest NBA game data...")
result1 = subprocess.run(['python', 'get_nba_data.py'], capture_output=True, text=True)
print(result1.stdout)

# Run project_props.py
print("\n[2/2] Rebuilding player projections...")
result2 = subprocess.run(['python', 'project_props.py'], capture_output=True, text=True)
print(result2.stdout)

# Count how many players we have projections for
try:
    proj_df = pd.read_csv('player_projections.csv')
    player_count = len(proj_df)
except:
    player_count = 0

# Send confirmation email
msg = MIMEText(f"""
NBA Data Daily Update Complete

Run Time: {datetime.now().strftime('%I:%M %p EST on %B %d, %Y')}

✓ Game data refreshed (includes last night's games)
✓ Player projections updated ({player_count} players)
✓ Ready for 5 PM edge analysis

Next update: Tomorrow at 3 PM
""")

msg['Subject'] = f"✓ NBA Data Updated - {datetime.now().strftime('%b %d, %I:%M %p')}"
msg['From'] = SENDER_EMAIL
msg['To'] = RECIPIENT_EMAIL

try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    server.send_message(msg)
    server.quit()
    print("\n✓ Confirmation email sent")
except Exception as e:
    print(f"\n✗ Email failed: {e}")

print(f"\n{'='*70}")
print("Update Complete")
print(f"{'='*70}\n")
