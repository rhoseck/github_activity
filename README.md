# GitHub User Activity

A command-line tool to fetch and display the recent activity of a GitHub user.

## Features

- Fetches a user's recent public activity from the GitHub API.
- Displays activity in a clean, readable format in the terminal.
- Includes relative timestamps for each event (e.g., "5 minutes ago").
- Supports filtering activity by event type (e.g., `PushEvent`, `PullRequestEvent`).
- Caches API responses for 10 minutes to improve performance and avoid rate limiting.

## Requirements

- Python 3.x

## Usage

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd github-user-activity
    ```

2.  **Run the script:**

    -   To fetch all recent activity for a user:
        ```bash
        python github_activity.py <username>
        ```
        **Example:**
        ```bash
        python github_activity.py octocat
        ```

    -   To filter activity by a specific event type:
        ```bash
        python github_activity.py <username> --filter <EventType>
        ```
        **Example (show only push events):**
        ```bash
        python github_activity.py octocat --filter PushEvent
        ```

## How It Works

The script makes a request to the GitHub API endpoint `https://api.github.com/users/<username>/events`. The JSON response is then parsed and formatted for display.

To improve performance, responses are cached in a local `.cache` directory for 10 minutes.