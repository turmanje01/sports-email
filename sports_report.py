import requests
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
import os

def get_scores():
    # ESPN's public APIs (Free, no keys needed)
    endpoints = {
        "Boston Red Sox": "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard",
        "Boston Celtics": "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard",
        "New England Patriots": "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard",
        "Georgia Bulldogs": "https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard"
    }

    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime("20181027")
    
    report_lines = [f"Daily Sports Report for {yesterday.strftime('20181027')}\n"]
    
    for team, url in endpoints.items():
        try:
            res = requests.get(f"{url}?dates={date_str}").json()
            played = False
            
            for event in res.get('events', []):
                if team in event['name']:
                    played = True
                    status = event['status']['type']['description']
                    
                    # Grab scores for both teams
                    comps = event['competitions'][0]['competitors']
                    team1 = comps[1]['team']['name']
                    score1 = comps[1].get('score', '')
                    team2 = comps[0]['team']['name']
                    score2 = comps[0].get('score', '')
                    
                    report_lines.append(f"✅ {team}: {status} ({team1} {score1} vs {team2} {score2})")
                    break
            
            if not played:
                report_lines.append(f"⏸️ {team}: Did not play yesterday.")
                
        except Exception:
            report_lines.append(f"⚠️ {team}: Data unavailable.")
            report_lines.append("\n--") 
    current_time = datetime.now().strftime("%b %d, %Y at %I:%M %p")
    report_lines.append(f"Report Generated: {current_time}")
            
    return "\n".join(report_lines)

def send_email(report_text):
    sender = os.environ.get("EMAIL_USER")
    password = os.environ.get("EMAIL_PASS")
    recipients_env = os.environ.get("EMAIL_RECIPIENTS")
    
    if not sender or not password or not recipients_env:
        print("Email credentials missing. Printing to console instead.")
        return
        
    recipients = [email.strip() for email in recipients_env.split(",")]
    
    msg = MIMEText(report_text)
    msg['Subject'] = "Daily Sports Report"
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)
    
    try:
        # Assuming Gmail's SMTP server here
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.sendmail(sender, recipients, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    report = get_scores()
    print(report)
    send_email(report)
