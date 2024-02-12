import json
import os
import redis
import requests
from openai import OpenAI
from github import Github
from urllib.parse import urlparse
from markdown_it import MarkdownIt
from urllib.parse import urljoin
from dotenv import load_dotenv


load_dotenv()  # load environment variables

client = OpenAI()  # initiliaze openai api
 
# initialize github api
GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN") 
GITHUB = Github(GITHUB_ACCESS_TOKEN)
GITHUB_API_BASE = "https://api.github.com/repos/"

# initialize database variables
UPSTASH_HOST = os.getenv("UPSTASH_HOST")  
UPSTASH_PORT = int(os.getenv("UPSTASH_PORT"))
UPSTASH_PASSWORD = os.getenv("UPSTASH_PASSWORD")

# connect to database
upstash = redis.Redis(
    host=UPSTASH_HOST,
    port=UPSTASH_PORT,
    password=UPSTASH_PASSWORD,
)

def main(repo_url):
    repo_identifier = parse_github_url(repo_url)
    
    if (is_up_to_date(repo_identifier)):
        return get_faq(repo_identifier)
        
    md_info = parse_markdown_files(repo_identifier,GITHUB_ACCESS_TOKEN,repo_url)
    
    if (md_info == -1):  # check if there exists any .md files
        return "There isn't any .md file in this repostory.Please check the link and repository."

    return create_faq(md_info,repo_identifier)    

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
    number_of_md = 0
    
    # extract text parts from md
    for content in contents:
        if content["type"] == "file" and content["name"].lower().endswith(".md"):
            file_url = content["download_url"]
            response = requests.get(file_url, headers=headers)
            response.raise_for_status()
            
            markdown_content = response.text
            parsed_content = md.parse(markdown_content)
            text = extract_text_from_markdown(parsed_content)
            extracted_info.append(text)
            number_of_md += 1
        
    return (extracted_info,number_of_md) if number_of_md != 0 else -1

def extract_text_from_markdown(parsed_content):
    text_content = []
    for node in parsed_content:
        text_content.append(node.content.strip()) 
    return "".join(text_content)

def chat(prompt,questions=""):
    message_history = []
    
    if questions != "":
        message_history.append({"role": "assistant", "content": "Generated FAQ and their answers are :\n"})
        message_history.append({"role": "assistant", "content": questions})
    
    message_history.append({"role": "user", "content": prompt})
    
    response = client.chat.completions.create(
        model = "gpt-3.5-turbo-0125",
        messages = message_history
    )
    return response

# generates faq for each md file
def generate_faq(md_files, number_of_md):
    faqs = []
    index = 1
    number_of_questions = 10 if number_of_md > 2 else 30//number_of_md
    for content in md_files:
        prompt = (
            f"Generate {number_of_questions} frequently asked questions (FAQ) for the following content."
            f"Then, rewrite the question you've chosen first as a title and after writing the question as a title, under that title, provide the answer to the question."
            f"Afterwards, repeat the same process for all generated questions one by one, rewriting the question first then answering the question under the question."
            f"I want these question and answer paragraphs enumerated, starting from {index} to {index + number_of_questions - 1}"
            f"For example:\n"
            f"{index}. How to write prompts?\n"
            f"In order to write prompts, you need to ....\n"
            f"{index + number_of_questions -1}. How to edit a written prompt?\n"
            f"Editing a prompt is easy, you need to.....\n"
            f"Content :\n{content}"
        )
        response = chat(prompt)
        faq = response.choices[0].message.content
        faqs.append(faq)
        index += number_of_questions
    return faqs

# chooses the most important faq from generated questioons 
def choose_faq(faqs):
    questions = "\n".join(faqs) 
    prompt = (
        f"Examine all generated FAQ and their answers, then reorder them by considiring the level of importance,from the most important one to least important one.\n"
        f"Write the first thirty questions and their answers from the ordered list."
    )
    response = chat(prompt,questions)
    return response.choices[0].message.content

# creates faq if the repo is updated or not in the database
def create_faq(md_info,repo_identifier):
    md_content = md_info[0]
    md_number = md_info[1]
    questions = generate_faq(md_content,md_number)
    faq = choose_faq(questions) 
    store_faq(repo_identifier,faq)
    return faq

# stores the chosen faq in database
def store_faq(repo_identifier,chosen_faq):
    last_commit = get_latest_commit_id(repo_identifier)
    value = (chosen_faq,last_commit)
    json_value = json.dumps(value)
    upstash.set(repo_identifier, json_value)

# checks if the repo is in database
def is_repo_in_database(repo_identifier):
    return upstash.exists(repo_identifier)

# compares latest commit id and checks if the repo is updated
def is_up_to_date(repo_identifier):
    if not is_repo_in_database(repo_identifier):
        return False
    
    json_value = upstash.get(repo_identifier)
    _, stored_last_commit = json.loads(json_value)
    current_commit = get_latest_commit_id(repo_identifier)
    return current_commit == stored_last_commit

# returns stored faq from the database
def get_faq(repo_identifier):
    json_value = upstash.get(repo_identifier)
    stored_faq, _ = json.loads(json_value)
    return stored_faq

# faq = main("https://github.com/ie310-hw-org/ie-hw-03")
# print(faq)
# upstash.close()
# upstash = None