import sys
import json
from urllib import request, error
import os
import time
from datetime import datetime, timedelta, timezone

CACHE_DIR = ".cache"
CACHE_DURATION_SECONDS = 600  # 10 minutes

def get_user_activity(username):
    """
    Fetches the recent activity of a GitHub user, using a cache.
    """
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    cache_path = os.path.join(CACHE_DIR, f"{username}.json")

    # Check cache
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            try:
                cache_data = json.load(f)
                cached_time = datetime.fromisoformat(cache_data['timestamp'])
                if datetime.now(timezone.utc) - cached_time < timedelta(seconds=CACHE_DURATION_SECONDS):
                    print("Fetching data from cache...")
                    return cache_data['events']
            except (json.JSONDecodeError, KeyError):
                # Invalid cache file, proceed to fetch
                pass

    # Fetch from API
    print("Fetching data from GitHub API...")
    api_url = f"https://api.github.com/users/{username}/events"
    try:
        with request.urlopen(api_url) as response:
            if response.status == 200:
                events = json.loads(response.read().decode())
                # Save to cache
                with open(cache_path, 'w') as f:
                    cache_content = {
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                        'events': events
                    }
                    json.dump(cache_content, f)
                return events
            else:
                print(f"Error: Unable to fetch data. Status code: {response.status}")
                return None
    except error.HTTPError as e:
        if e.code == 404:
            print(f"Error: User '{username}' not found.")
        else:
            print(f"Error: API request failed. {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def display_activity(events, filter_type=None):
    """
    Displays the fetched GitHub activity in a readable format.
    """
    if not events:
        print("No recent activity to display.")
        return

    print("\nRecent GitHub Activity:")
    for event in events:
        event_type = event.get('type')
        if filter_type and filter_type.lower() != event_type.lower():
            continue

        repo_name = event.get('repo', {}).get('name')
        payload = event.get('payload', {})
        created_at_str = event.get('created_at')
        
        # Format timestamp
        timestamp = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
        time_ago = datetime.now(timezone.utc) - timestamp
        
        if time_ago.days > 0:
            time_str = f"{time_ago.days} days ago"
        elif time_ago.seconds // 3600 > 0:
            hours = time_ago.seconds // 3600
            time_str = f"{hours} hours ago"
        else:
            minutes = time_ago.seconds // 60
            time_str = f"{minutes} minutes ago"

        message = ""
        if event_type == 'PushEvent':
            commit_count = len(payload.get('commits', []))
            message = f"Pushed {commit_count} commits to {repo_name}"
        elif event_type == 'CreateEvent':
            ref_type = payload.get('ref_type')
            message = f"Created a new {ref_type} in {repo_name}"
        elif event_type == 'IssuesEvent':
            action = payload.get('action')
            issue_title = payload.get('issue', {}).get('title')
            message = f"{action.capitalize()} issue '{issue_title}' in {repo_name}"
        elif event_type == 'IssueCommentEvent':
             message = f"Commented on an issue in {repo_name}"
        elif event_type == 'PullRequestEvent':
            action = payload.get('action')
            pr_title = payload.get('pull_request', {}).get('title')
            message = f"{action.capitalize()} pull request '{pr_title}' in {repo_name}"
        elif event_type == 'WatchEvent':
            action = payload.get('action')
            message = f"{action.capitalize()} watching {repo_name}"
        else:
            message = f"{event_type} on {repo_name}"
        
        print(f"- [{time_str}] {message}")


if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 4:
        print("Usage: python github_activity.py <username> [--filter <EventType>]")
        sys.exit(1)

    username = sys.argv[1]
    event_filter = None

    if len(sys.argv) == 4 and sys.argv[2].lower() == '--filter':
        event_filter = sys.argv[3]

    user_events = get_user_activity(username)

    if user_events:
        display_activity(user_events, filter_type=event_filter)
