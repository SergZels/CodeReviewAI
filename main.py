from fastapi import FastAPI, Request, Form
from pydantic import BaseModel, validator, field_validator
import re
from enum import Enum
from businessLogic import logger, GitHubRepoManager, GITHUB_TOKEN, MODEL, get_prompt, get_code_review

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

class Answer(BaseModel):
    file_paths: list[str]
    prompt: str
    GPTReview: str = None

@app.post('/review', response_model=Answer)
async def review(review_request: Review):
    github_url = review_request.github_repo_url
    file_paths = []
    prompt = ""

    try:
        repo_manager = GitHubRepoManager(github_url, GITHUB_TOKEN)
        file_paths, all_content = await repo_manager.clone_repo()

        code_content = all_content
        candidate_level = review_request.candidate_level
        description = review_request.assignment_description
        prompt = get_prompt(code_content=code_content,
                            description=description,
                            candidate_level=candidate_level)


    except Exception as e:
        print(e)
        logger.error(f"Error occurred during processing {e}")

    try:
        review_result = get_code_review(prompt=prompt, model=MODEL)
    except Exception as e:
        print(e)
        review_result = f"Error occurred during processing {e}"
        logger.error(f"Error occurred during processing {e}")

    answer = Answer(file_paths=file_paths, prompt=prompt, GPTReview=review_result)

    return answer
