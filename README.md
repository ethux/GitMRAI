# GitMRAI 🚀

GitMRAI is a work-in-progress hobby project designed to automate the creation of reviews and summaries for GitLab Merge Requests. The goal is to replicate some of the features offered by 'GitLab Duo', but with a completely open-source and free-to-use approach. Note that there are still some bugs to iron out! 🐞

## ✨ Features

At this moment, GitMRAI offers three endpoints that can be triggered by GitLab webhooks on Merge Request push events:

1. **Summarize the changes in a new comment within the Merge Request:**
   - `/api/v1/mr_summarize`
2. **Update the current description of the Merge Request with a summary:**
   - `/api/v1/mr_description`
3. **Create a comment on a specific part of the Merge Request diff/changes:**
   - `/api/v1/mr_comment_on_diff`

## 🛠️ Installation

### Prerequisites
- Python 3.10+
- GitLab account with access to the repository or group
- Mistral AI API key

### Steps

1. **Clone the repository:**
   ```sh
   git clone https://github.com/ethux/GitMRAI.git
   cd GitMRAI
   ```

2. **Create a virtual environment and activate it:**
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the required dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the root directory and add the following variables:
   ```env
   MODEL=<mistral_ai_model>
   API_KEY=<mistral_api_key>
   GITLAB_URL=<gitlab_url>
   GITLAB_TOKEN=<gitlab_access_token_for_repo_or_group>
   SECRET_TOKEN=<secret_token_for_api_auth> # This token should be added to the GitLab webhook config as the GitLab secret auth token.
   ```

5. **Run the application:**
   ```sh
   uvicorn main:app --host 0.0.0.0 --port 8080
   ```

### 🐳 Docker Compose

To simplify the deployment process, you can use Docker Compose. This will build and run the application in a Docker container.

#### Prerequisites
- Docker
- Docker Compose

#### Steps

1. **Clone the repository:**
   ```sh
   git clone https://github.com/ethux/GitMRAI.git
   cd GitMRAI
   ```

2. **Create a `.env` file in the root directory and add the necessary environment variables:**
   ```env
   MODEL=<mistral_ai_model>
   API_KEY=<mistral_api_key>
   GITLAB_URL=<gitlab_url>
   GITLAB_TOKEN=<gitlab_access_token_for_repo_or_group>
   SECRET_TOKEN=<secret_token_for_api_auth> # This token should be added to the GitLab webhook config as the GitLab secret auth token.
   ```

3. **Build and run the application using Docker Compose:**
   ```sh
   docker-compose up --build
   ```
   This will build the Docker image and start the container, exposing the application on port 8080.

## 🔧 Configuration

### GitLab Webhook Setup

1. Navigate to your GitLab repository or group settings.
2. Go to **Webhooks**.
3. Add a new webhook:
   - **URL**: `http://your-server-ip:8080/api/v1/mr_summarize` (or the respective endpoint)
   - **Secret Token**: Use the `SECRET_TOKEN` from your `.env` file.
   - **Trigger**: Select **Merge Request events**.

## 🎈 Usage

Once the webhook is set up, any push event on a Merge Request will trigger the respective endpoint, generating a summary or comment based on the changes.

You can also change the prompts within the JSON files to adjust the summarize style or prompt to your wishes:
- `system_prompt_summarize.json`
- OR
- `system_prompt.json`

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## 📜 License

This project is licensed under the MIT License. See the LICENSE file for details.