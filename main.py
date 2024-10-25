from fastapi import FastAPI, Request, Form
from pydantic import BaseModel, validator, field_validator
import re
from enum import Enum
from dotenv import load_dotenv
from businessLogic import logger, GitHubRepoManager

load_dotenv()
app = FastAPI()


class CandidateLevel(str, Enum):
    JUNIOR = 'Junior'
    MIDDLE = 'Middle'
    SENIOR = 'Senior'

class Review(BaseModel):
    assignment_description: str
    github_repo_url: str
    candidate_level: CandidateLevel

    @field_validator('github_repo_url')
    def validate_github_url(cls, value):
        github_pattern = re.compile(r'^https://github\.com/.+/.+$')
        if not github_pattern.match(value):
            raise ValueError('The URL must be a valid GitHub repository link.')
        return value


@app.post('/review', response_model=Review)
async def review(review_request:Review):
    github_url = 'https://github.com/SergZels/MidjourneyFlaskProject.git'
    github_token = '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'

    repo_manager = GitHubRepoManager(github_url, github_token)
    file_paths, all_content = await repo_manager.clone_repo()

    print("Список файлів:")
    print(file_paths)

    print("\nВміст файлів:")
    print(all_content)

    return review_request

