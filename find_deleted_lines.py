import requests
import re
import collections

GITHUB_TOKEN = "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"


def find_deleted_lines(patch):
    patch_lines_all = patch.split('\n')

    patch_lines=patch_lines_all[1:]

    patch_lines.pop()
    queue=collections.deque()
    dump=[]
    for p in patch_lines:
        if p[0]=='-':
            queue.append(p[1:])
        elif p[0]=='+':
            if len(queue):
                queue.popleft()
        else:
            if len(queue):
                while len(queue)>0:
                    q=queue.popleft()
                    dump.append(q)
    return dump

def identify_commits_with_deletions(commits):
    deletions_list = []

    for commit in commits:
        commit_url = commit["url"]
        commit_sha=commit["sha"]
        print(commit_sha)
        committer_email = commit["commit"]["author"]["email"]

        # Get commit details
        commit_details_response = requests.get(
            commit_url, headers={"Authorization": f"token {GITHUB_TOKEN}"}
        )
        commit_details = commit_details_response.json()

        # Checking if there are only deletions and no or some additions
        total_changes = commit_details["stats"]["total"]
        deletions = commit_details["stats"]["deletions"]
        additions = commit_details["stats"]["additions"]
        commit_files = commit_details["files"]
        if deletions > 0 and additions >= 0:
            # check for deletions in files
            patch_files = {}
            files_to_check = ["pr-data.csv", "gr-data.csv"]
            for file in commit_files:

              
                if file["filename"] in files_to_check:
                    deleted_lines = find_deleted_lines(file["patch"])
                    if len(deleted_lines):
                        deletions_list.append(
                                (committer_email, commit_sha, deleted_lines)
                            )

    return deletions_list


def get_commits(repo_owner, repo_name, since_date):
    flag=True
    commits_data=[]
    page=1
    while flag:
        api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits?since={since_date}&per_page=100&page={page}"

        headers = {"Authorization": f"token {GITHUB_TOKEN}","Accept": "application/vnd.github.v3+json"}

        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            d = response.json()
            if len(d)==0:
                flag=False
            for data in d:
                commits_data.append(data)
            page+=1
            
        else:
            flag=False
            return response 
    return commits_data
def print_deletions_list(deletions_list):
    for committer_email, commit_sha, patch_line in deletions_list:
        print(
            f"Committer Email: {committer_email}, Deleted Lines: {patch_line}, Commit URL: {commit_sha},"
        )


if __name__ == "__main__":
    repo_owner = "TestingResearchIllinois"
    repo_name = "idoft"
    since_date = "2023-08-15T00:00:00Z"

    commits = get_commits(repo_owner, repo_name, since_date)
    deletions_list = identify_commits_with_deletions(commits)
    print_deletions_list(deletions_list)
