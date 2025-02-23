# GitMRAI 🚀

GitMRAI is a Work In Progress hobby project designed to automate the creation of reviews and summaries for Gitlab Merge Requests. The goal is to replicate the features of 'Gitlab DUO' but with a completely Open Source and free-to-use approach. Note that there are still some bugs to iron out! 🐞

## ✨ Features

At this moment, GitMRAI offers three endpoints that can be triggered by Gitlab webhooks on Merge Request push events:

1. **Summarize the changes in a new comment within the Merge Request:**
   - `/api/v1/mr_summarize`

2. **Update the current description of the Merge Request with a summary:**
   - `/api/v1/mr_description`

3. **Create a comment on a specific part of the Merge Request diff/changes:**
   - `/api/v1/mr_comment_on_diff`

## 🛠️ Installation

### Prerequisites

- Python 3.10+
- Gitlab account with access to the repository or group
- Mistral AI API key

### Steps

1. **Clone the repository:**

   ```sh
   git clone https://github.com/ethux/GitMRAI.git
   cd GitlabMRAI
   ```

2. **Create a virtual environment and activate it:**

   ```sh
   python3 -m venv venv
   source venv/bin/activate # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   - Create a `.env` file in the root directory and add the following variables:

   ```dotenv
   MODEL=<mistral_ai_model>
   API_KEY=<mistral_api_key>
   GITLAB_URL=<gitlab_url>
   GITLAB_TOKEN=<gitlab_access_token_for_repo_or_group>
   SECRET_TOKEN=<secret_token_for_api_auth> # This token should be added to the Gitlab webhook config as the Gitlab secret auth token.
   ```

5. **Run the application:**

   ```sh
   uvicorn main:app --host 0.0.0.0 --port 8080
   ```

## 🔧 Configuration

### Gitlab Webhook Setup

1. Navigate to your Gitlab repository or group settings.
2. Go to **Webhooks**.
3. Add a new webhook:
   - **URL:** `http://your-server-ip:8080/api/v1/mr_summarize` (or the respective endpoint)
   - **Secret Token:** Use the `SECRET_TOKEN` from your `.env` file.
   - **Trigger:** Select **Merge Request events**.

## 🎈 Usage

Once the webhook is set up, any push event on a Merge Request will trigger the respective endpoint, generating a summary or comment based on the changes.

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

This README provides a clear guide for installing, setting up, and using GitMRAI. It also includes instructions for configuring Gitlab webhooks to trigger the application's endpoints.