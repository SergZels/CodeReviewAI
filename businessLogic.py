import os
import git
from dotenv import load_dotenv
import logging
import tempfile
import aiofiles
import asyncio
from openai import AsyncOpenAI,OpenAI

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPENAI_TOKEN = os.getenv("OPENAI_TOKEN")

class AsyncFileHandler(logging.FileHandler):
    def emit(self, record):
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, super().emit, record)


logger = logging.getLogger('async_logger')
logger.setLevel(logging.INFO)
handler = AsyncFileHandler('Logfile.txt')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

#----------------------------GitHub------------------------------------------------------------------
class GitHubRepoManager:
    def __init__(self, github_url, github_token):
        self.github_url = github_url
        self.github_token = github_token
        self.owner, self.repo = self.extract_owner_repo_from_url()

    def extract_owner_repo_from_url(self):
        parts = self.github_url.rstrip(".git").split('/')
        owner = parts[-2]
        repo = parts[-1]
        return owner, repo

    async def clone_repo(self):
        tokenized_url = self.github_url.replace('https://', f'https://{self.github_token}@')

        with tempfile.TemporaryDirectory() as tmpdirname:
            print(f"Клонування в тимчасову директорію {tmpdirname}")

            git.Repo.clone_from(tokenized_url, tmpdirname)
            file_paths, all_content = await self.list_files_and_content(tmpdirname)

            return file_paths, all_content

    async def list_files_and_content(self, local_repo_path):
        file_paths = []
        all_content = ""

        for root, dirs, files in os.walk(local_repo_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, local_repo_path)
                file_paths.append(relative_path)

                async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = await f.read()
                    all_content += f"\n\n--- {relative_path} ---\n\n{content}"

        return file_paths, all_content

#------------------------------OpenAI--------------------------------------------------------------------

client = OpenAI(api_key=OPENAI_TOKEN)
def get_code_review(code_content:str, candidate_level:str, description:str, model:str):
    prompt = f"""
    You are an expert code reviewer. The code below is written by a {candidate_level} developer.
    Here is the task description:
    {description}

    Code:
    {code_content}

    Please provide:
    1. A list of key problems in one paragraph.
    2. A rating out of 5 for a {candidate_level} developer.
    3. A conclusion regarding the overall quality and what the developer can improve.
    """

    response = client.chat.completions.create(
        model= model,#"gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a senior software engineer tasked with reviewing code."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=500,
        temperature=0.7,
    )

    return response['choices'][0]['message']['content']
