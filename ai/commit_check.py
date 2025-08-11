import os, requests, datetime
REPO  = os.getenv("GITHUB_REPOSITORY","")
token = os.getenv("GITHUB_TOKEN")
hook  = os.getenv("SLACK_WEBHOOK_URL")

def gh(url):
    h = {"Authorization": f"Bearer {token}",
         "Accept": "application/vnd.github+json"}
    r = requests.get(url, headers=h)
    r.raise_for_status()
    return r.json()

since = (datetime.datetime.utcnow() - datetime.timedelta(days=1)).isoformat()+"Z"
commits = gh(f"https://api.github.com/repos/{REPO}/commits?since={since}")
if not commits:
    msg = f"⏰ No commits in the last 24h to {REPO}. Do one tiny commit now."
    if hook:
        requests.post(hook, json={"text": msg})
