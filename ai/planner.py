import os, json, requests, datetime

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GITHUB_TOKEN   = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPOSITORY", "")  # Provided by Actions

def gh(url, method="GET", **kw):
    h = {"Authorization": f"Bearer {GITHUB_TOKEN}",
         "Accept": "application/vnd.github+json"}
    r = requests.request(method, url, headers=h, **kw)
    r.raise_for_status()
    return r.json()

def fetch_issues():
    return gh(f"https://api.github.com/repos/{REPO}/issues?state=open&per_page=100")

def fetch_commits():
    since = (datetime.datetime.utcnow() - datetime.timedelta(days=7)).isoformat()+"Z"
    return gh(f"https://api.github.com/repos/{REPO}/commits?since={since}&per_page=100")

def openai_chat(prompt):
    import openai
    openai.api_key = OPENAI_API_KEY
    sys_prompt = "You write ultra-concise, execution-ready daily plans."
    resp = openai.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role":"system","content":sys_prompt},
                  {"role":"user","content":prompt}],
        temperature=0.2, max_tokens=700
    )
    return resp.choices[0].message.content.strip()

def create_issue(title, body):
    payload = {"title": title, "body": body}
    gh(f"https://api.github.com/repos/{REPO}/issues", method="POST", json=payload)

if __name__ == "__main__":
    issues  = fetch_issues()
    commits = fetch_commits()
    prompt = f"""Summarize and plan.
Issues:
{json.dumps([{k: i.get(k) for k in ["title","number","labels"]} for i in issues], indent=2)}
Commits (last 7d):
{json.dumps([c.get("commit",{}).get("message","") for c in commits][:50], indent=2)}
Use this template:
{open('ai/prompts/daily_planner.md','r',encoding='utf-8').read()}
"""
    plan = openai_chat(prompt)
    today = datetime.date.today().isoformat()
    create_issue(f"Daily Focus — {today}", plan)
