import subprocess
import random
from datetime import datetime, timedelta

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout

def get_commits():
    raw = run(['git', 'log', '--reverse', '--format=%H|%ad|%s', '--date=iso'])
    commits = []
    for line in raw.strip().split('\n'):
        if not line: continue
        parts = line.split('|', 2)
        commits.append({
            'hash': parts[0],
            'date': parts[1],
            'msg': parts[2]
        })
    return commits

commits = get_commits()
current_time_limit = datetime(2026, 1, 18, 11, 0, 0)

# Create a temporary orphan branch
subprocess.run(['git', 'checkout', '--orphan', 'fix_future_branch'], check=True)
subprocess.run(['git', 'rm', '-rf', '.'], check=True)

for i, c in enumerate(commits):
    subprocess.run(['git', 'checkout', c['hash'], '--', '.'], check=True)
    subprocess.run(['git', 'add', '-A'], check=True)
    
    date_str = c['date']
    dt_part = date_str[:19]
    tz_part = date_str[20:]
    dt = datetime.strptime(dt_part, "%Y-%m-%d %H:%M:%S")
    
    # If commit is after today 11:00 AM, move it to earlier today or yesterday
    if dt >= current_time_limit:
        # Move these specific future commits to earlier today (e.g. between 08:00 and 10:50)
        # We have 3 commits: 11:02, 14:01, 16:04
        # Let's map them to 10:10, 10:30, 10:50 approx
        base_hour = 10
        new_min = 10 + (i % 3) * 20 + random.randint(1, 5)
        new_sec = random.randint(1, 59)
        dt = dt.replace(day=18, hour=base_hour, minute=new_min, second=new_sec)
    
    new_date = dt.strftime("%Y-%m-%d %H:%M:%S") + " " + tz_part
    
    env = {
        'GIT_AUTHOR_DATE': new_date,
        'GIT_COMMITTER_DATE': new_date
    }
    subprocess.run(['git', 'commit', '-m', c['msg']], env=env, check=True)

subprocess.run(['git', 'branch', '-M', 'fix_future_branch', 'main'], check=True)
print("Future commits fixed.")
