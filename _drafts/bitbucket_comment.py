import os
import argparse
import requests # type: ignore

def get_bitbucket_credentials():
    username = os.getenv("DANGER_BITBUCKETCLOUD_USERNAME")
    password = os.getenv("DANGER_BITBUCKETCLOUD_PASSWORD")
    return username, password

def get_pr_info():
    parser = argparse.ArgumentParser(description="Bitbucket PR Task Manager")
    parser.add_argument("--workspace", required=True, help="Bitbucket workspace name")
    parser.add_argument("--repo_slug", required=True, help="Bitbucket repository slug")
    parser.add_argument("--pr_id", required=True, help="Bitbucket pull request ID")
    parser.add_argument("--pr_author_id", required=False, help="Bitbucket pull request author")
    parser.add_argument("--comment_title", required=True, help="Bitbucket pull request title")
    parser.add_argument("--file_path", required=True, help="Bitbucket pull request title")
    args = parser.parse_args()
    return args.workspace, args.repo_slug, args.pr_id, args.pr_author_id, args.comment_title, args.file_path

def get_all_comment_ids(username, password, url):
    response = requests.get(url, auth=(username, password))
    list = []
    if response.status_code == 200:
        comments = response.json().get("values", [])
        for comment in comments:
            list.append(comment["id"])
    else:
        print(f"Failed to fetch PR comments\n{response}")
    return list

def delete_comment(username, password, url):
    response = requests.delete(url, auth=(username, password))
    if response.status_code == 204:
        print(f'Delete comment successfully')
    else:
        print(f"Failed to delete PR comments\n{response}")

def get_comment_id(username, password, url, comment_title):
    response = requests.get(url, auth=(username, password))
    comment_id = None
    if response.status_code == 200:
        comments = response.json().get("values", [])
        for comment in comments:
            if comment["content"]["raw"].startswith(comment_title):
                comment_id = comment["id"]
                break
        if comment_id is None:
            next_url = response.json().get("next")
            if next_url:
                # load next page
                return get_comment_id(username, password, next_url, comment_title)
    else:
        print(f"Failed to fetch PR comments\n{response}")
    return comment_id

def get_comment_contents(comment_title, pr_author_id, file_path):
    comment = comment_title
    if pr_author_id:
        comment += f"@{{{pr_author_id}}}"
    if file_path:
        with open(file_path, 'r') as report_file:
            content = report_file.read()
        #string = f"{comment_title}\n\n<details>\n<summary>Details</summary>\n\n{content}\n</details>"
        string = f"""
        {comment_title}

        <details>

        <summary>Tips for collapsed sections</summary>

        ### You can add a header

        You can add text within a collapsed section. 

        You can add an image or a code block, too.

        ```ruby
        puts "Hello World"
        ```

        </details>
        """
        comment = {
            "content": {
                "raw": string
            }
        }
    return comment

def create_comment(username, password, pr_id, url, comment_contents, pr_author_id, file_path):
    comment_data = get_comment_contents(comment_contents, pr_author_id, file_path)
    response = requests.post(url, json=comment_data, auth=(username, password))
    if response.status_code == 201:
        comment_id = response.json()["id"]
        return comment_id
    else:
        print(f"Error: Unable to create comment for PR {pr_id}\n{response}")
        return None

def update_comment(username, password, url, comment_contents, comment_id, pr_author_id, file_path):
    print("Updating the comment...")
    update_comment_url = f"{url}/{comment_id}"
    data = get_comment_contents(comment_contents, pr_author_id, file_path)
    response = requests.put(update_comment_url, json=data, auth=(username, password))
    if response.status_code == 200:
        print(f"Updating the comment finished.")
    else:
        print(f"Error: Unable to update comment\n{response}")

def main():
    username, password = get_bitbucket_credentials()
    workspace, repo_slug, pr_id, pr_author_id, comment_title, file_path = get_pr_info()

    comments_url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}/comments"

    # list = get_all_comment_ids(username, password, comments_url)
    # for id in list:
    #     url = comments_url + f"/{id}"
    #     delete_comment(username, password, url)

    print("Getting the comment...")
    comment_id = get_comment_id(username, password, comments_url, comment_title)
    if comment_id:
        print('Update existing comment...')
        update_comment(username, password, comments_url, comment_title, comment_id, pr_author_id, file_path)
    else:
        print("There is no specified comment, creating a new one...")
        create_comment(username, password, pr_id, comments_url, comment_title, pr_author_id, file_path)

if __name__ == "__main__":
    main()
