# Auto Review Tools
This tool will help you automate the process of reviewing code

## Installation
You must have it installed Git and Docker
1. Clone the repository:
   ```bash
   git clone https://github.com/SergZels/CodeReviewAI.git
   cd CodeReviewAI
2. Edit the .env file by entering your tokens for GitHub and OpenAI before running the next command.
3. ```bash
   docker compose up -d
  
5. Open your browser and navigate to:
   [http://127.0.0.1:7777/](http://127.0.0.1:7777/)

![alt text](image-1.png)

6. You can also use the API by sending `POST` requests to:
   [http://127.0.0.1:7777/review](http://127.0.0.1:7777/review)

   Here is the format of the request body:
   ```json
   {
     "assignment_description": "string",
     "github_repo_url": "https://github.com/SergZels/gameBot.git",
     "candidate_level": "Junior"
   }
   Here is an example of an answer
![alt text](image.png)


  

