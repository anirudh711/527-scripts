import requests
import csv

# https://api.github.com/repos/{pr_url.split("/")[3]}/{pr_url.split("/")[4]}/pulls/{pr_number}

# Replace 'YOUR_GITHUB_TOKEN' with your actual GitHub token
GITHUB_TOKEN = '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'

def check_pr_status(pr_url):
    pr_number = pr_url.split('/')[-1]
    api_url = f'https://api.github.com/repos/{pr_url.split("/")[3]}/{pr_url.split("/")[4]}/pulls/{pr_number}'

    # Include the token in the headers
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        pr_data = response.json()
        pr_status = pr_data['state']
        pr_merged = pr_data['merged']
        
        return pr_status, pr_merged
    else:
        return f"API request failed with status code: {response.status_code}", None

def main():
    input_file = 'pr-data.csv'
    output_file = 'pr-data-statuses-out.csv'

    with open(input_file, 'r') as csvfile, open(output_file, 'w', newline='') as outfile:
        csvreader = csv.DictReader(csvfile)
        fieldnames = csvreader.fieldnames + ['PR Status', 'PR Merged']
        csvwriter = csv.DictWriter(outfile, fieldnames=fieldnames)
        csvwriter.writeheader()

        for row in csvreader:
            pr_url = row['PR Link']
            pr_status, pr_merged = "Empty","Empty"
            if pr_url:
                pr_status, pr_merged = check_pr_status(pr_url)
                print(row['Status'],pr_status, pr_merged)
            row['PR Status'] = pr_status
            row['PR Merged'] = pr_merged
           
            csvwriter.writerow(row)

if __name__ == "__main__":
    main()
