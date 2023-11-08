import requests
import csv

## This script is used to scan IDOFT and distinguish between PRs that have to be merged and PRs that should not be merged
## For the PRs that are not to be merged, further investigation has to be done to determine whether it is "InspiredAFix" or "Rejected"

# Replace 'YOUR_GITHUB_TOKEN' with your actual GitHub token
GITHUB_TOKEN = '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'

def check_pr_status(pr_url):
    pr_number = pr_url.split('/')[-1]
    api_url = f'https://api.github.com/repos/{pr_url.split("/")[3]}/{pr_url.split("/")[4]}/pulls/{pr_number}'

    headers = {'Authorization': f'token {GITHUB_TOKEN}'}

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        pr_data = response.json()
        pr_status = pr_data['state']
        pr_merged = pr_data['merged']
        
        return pr_status, pr_merged
    else:
        return f"API request failed with status code: {response.status_code}", None

def get_pr_comments_check_bot(pr_url):
    pr_number = pr_url.split('/')[-1]
    api_url = f'https://api.github.com/repos/{pr_url.split("/")[3]}/{pr_url.split("/")[4]}/issues/{pr_number}/comments'

    # Include the token in the headers
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}

    response = requests.get(api_url, headers=headers)
    users=[]
    if response.status_code == 200:
        comments_data = response.json()
        for comment in comments_data:
            if comment['user']['login']:
                users.append(comment['user']['login'])
        return users
    else:
        return []

def get_pr_comments(pr_url):
    pr_number = pr_url.split('/')[-1]
    api_url = f'https://api.github.com/repos/{pr_url.split("/")[3]}/{pr_url.split("/")[4]}/issues/{pr_number}/comments'

    # Include the token in the headers
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        comments_data = response.json()
        # print(scomments_data)
        for comment in comments_data:
            print(comment['user']['login'])
        return [comment['body'] for comment in comments_data]
    else:
        return []

def get_pr_review_comments(pr_url):
    pr_number = pr_url.split('/')[-1]
    api_url = f'https://api.github.com/repos/{pr_url.split("/")[3]}/{pr_url.split("/")[4]}/pulls/{pr_number}/comments'

    headers = {'Authorization': f'token {GITHUB_TOKEN}'}

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        comments_data = response.json()
       
        return [comment['body'] for comment in comments_data]
    else:
        return []

def determine_pr_status(pr_url):
    # Get comments and review comments for the PR
    pr_comments = get_pr_comments(pr_url)
    review_comments = get_pr_review_comments(pr_url)
    # botlist = get_pr_comments_check_bot(pr_url)

    # rejected_keywords = ["pull request has been closed", "stale","Closing","Closing ticket","Closing PR"]
    # if any(keyword in comment.lower() for comment in pr_comments for keyword in rejected_keywords) and  "github-actions[bot]" in botlist : 
    #     return "Rejected"

    # Check for "Rejected" status
    rejected_keywords = ["pull request has been closed", "stale","Closing","Closing ticket","Closing PR"]
    if any(keyword in comment.lower() for comment in pr_comments for keyword in rejected_keywords) or len(pr_comments)==0 or len(review_comments) == 0:
        return "Rejected"

    # Check for "InspiredAFix" status
    inspired_keywords = ["merged", "Merged"]
    if (
        any(keyword in comment.lower() for comment in review_comments for keyword in inspired_keywords) or 
        any(keyword in comment.lower() for comment in pr_comments for keyword in inspired_keywords)) and len(review_comments) > 0:
        return "InspiredAFix"

    # Default status if not determined
    return "Undetermined"

def main():
    input_file = './csv/pr-data.csv'
    output_file = './outs/filtered_data_anamolous-out.csv'

    with open(input_file, 'r') as csvfile, open(output_file, 'w', newline='') as outfile:
        csvreader = csv.DictReader(csvfile)
        fieldnames = csvreader.fieldnames
        csvwriter = csv.DictWriter(outfile, fieldnames=fieldnames)
        csvwriter.writeheader()

        for row in csvreader:
            pr_url = row['PR Link']
            if pr_url:
                pr_status, pr_merged = check_pr_status(pr_url)
     
                if row['Status'] == "Opened" and pr_status == "closed" and pr_merged == True:
                    print(row['Status'],pr_status, pr_merged,"--","Accepted",row['PR Link'])
                    row['Status'] = 'Accepted'
                if row['Status'] == "Opened" and pr_status == "closed" and pr_merged == False:
                    pr_status = determine_pr_status(pr_url)
                    print(row['Status'],pr_status, pr_merged,"--",pr_status, row['PR Link'])
                    row['Status'] = pr_status          
                
            csvwriter.writerow(row)

if __name__ == "__main__":
    main()
