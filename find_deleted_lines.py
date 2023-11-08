import requests
import datetime

# Please replace here with your token
GITHUB_TOKEN = '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'

def get_commits(repo_owner, repo_name, since_date, until_date):
    api_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/commits'
    params = {'since': since_date, 'until': until_date}
    
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}

    response = requests.get(api_url, headers=headers, params=params)

    if response.status_code == 200:
        commits_data = response.json()
        return commits_data
    else:
        return []

def identify_commits_with_deletions(commits):
    deletions_list = []

    for commit in commits:
        commit_url = commit['url']
        committer_email = commit['commit']['author']['email']

        # Get commit details
        commit_details_response = requests.get(commit_url, headers={'Authorization': f'token {GITHUB_TOKEN}'})
        commit_details = commit_details_response.json()

        # Checking if there are only deletions and no or some additions
        total_changes = commit_details['stats']['total']
        deletions = commit_details['stats']['deletions']
        additions = commit_details['stats']['additions']

        if deletions>0 and additions>=0:
            deletions_list.append((committer_email, deletions, commit_url))

    return deletions_list

def print_deletions_list(deletions_list):
    for committer_email, deleted_lines, commit_url in deletions_list:
        print(f"Committer Email: {committer_email}, Deleted Lines: {deleted_lines}, Commit Link: {commit_url}")

if __name__ == "__main__":
    repo_owner = 'TestingResearchIllinois'
    repo_name = 'idoft'
    since_date = '2022-01-01T00:00:00Z'  # Replace with your start date
    until_date = '2023-10-31T23:59:59Z'  # Replace with your end date

    commits = get_commits(repo_owner, repo_name, since_date, until_date)
    deletions_list = identify_commits_with_deletions(commits)
    print_deletions_list(deletions_list)
