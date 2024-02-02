import os
import redis
import requests
from openai import OpenAI
from github import Github
from urllib.parse import urlparse
from markdown_it import MarkdownIt
from urllib.parse import urljoin
from dotenv import load_dotenv
from upstash_redis import Redis


load_dotenv()  # load environment variables
client = OpenAI()  # initiliaze openai api
GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")  # initialize github api
GITHUB = Github(GITHUB_ACCESS_TOKEN)
GITHUB_API_BASE = "https://api.github.com/repos/"


# parse the repo link into username and repo name parts
# then create repo identifier
def parse_github_url(repository_url):
    parsed_url = urlparse(repository_url)
    path_parts = parsed_url.path.strip('/').split('/')
    if len(path_parts) == 2:
        return f"{path_parts[0]}/{path_parts[1]}"
    else:
        raise ValueError("Invalid GitHub repository URL")

# get last commit id. Will be used to check if the repo is updated
def get_latest_commit_id(repository_identifier):
    repo = GITHUB.get_repo(repository_identifier)
    latest_commit = repo.get_commits()[0]
    return latest_commit.sha

# find md files and parse the text parts
def parse_markdown_files(repo_identifier, github_token,repo_url):
    repo_url = urljoin(GITHUB_API_BASE, repo_identifier)
    headers = {"Authorization": f"token {github_token}"}

    contents_url = f"{repo_url}/contents"
    response = requests.get(contents_url, headers=headers)
    response.raise_for_status()
    contents = response.json()

    md = MarkdownIt()
    extracted_info = []

    # extract text parts from md
    for content in contents:
        if content["type"] == "file" and content["name"].lower().endswith(".md"):
            file_url = content["download_url"]
            response = requests.get(file_url, headers=headers)
            response.raise_for_status()
            
            markdown_content = response.text
            parsed_content = md.parse(markdown_content)
            extracted_info.append(extract_text_from_markdown(parsed_content))
            
    return extracted_info

def extract_text_from_markdown(parsed_content):
    text_content = []
    for node in parsed_content:
        text_content.append(node.content.strip()) 
    return "".join(text_content)

def chat(prompt):
    response = client.chat.completions.create(
            model = "gpt-3.5-turbo",
            messages = [
                {
                "role": "user", 
                "content": prompt
                }
            ]
        )
    return response

def generate_faq(md_files,faqs):
    for content in md_files:
        prompt = f"Generate 10 frequently asked questions (FAQ) for the following content:\n\n{content}\n"
        response = chat(prompt)
        faq = response.choices[0].message.content
        faqs.append(faq)
        
    return faqs

def choose_faq(faqs):
    questions = "\n".join(faqs)
    prompt_template = (
        "Choose the most important 30 questions from the following and answer them:\n\n"
        "{questions}\n"
    )
    prompt = prompt_template if len(faqs) > 3 else f"Answer these questions and enumerate them:\n\n{questions}\n"
    response = chat(prompt)    
    return response.choices[0].message.content


repository_url = 'https://github.com/ie310-hw-org/ie-hw-02'
repo_identifier = parse_github_url(repository_url)
markdown_info = parse_markdown_files(repo_identifier, GITHUB_ACCESS_TOKEN,repository_url)
list = []
generate_faq(markdown_info,list)
print(list)


