Repository: Internship-AI-Agent

Description:
No description

Language:
Python

Topics:


Stars:
0

Repository URL:
https://github.com/Manas-Dikshit/Internship-AI-Agent

README:

﻿# Internship Application Agent 🚀

An intelligent, automated agent designed to streamline your internship search. This tool searches for relevant internship opportunities, identifies contact emails (using smart fallback strategies), generates highly personalized cover letters using AI, and sends applications automatically.

## ✨ Features

- **Advanced Job Search**: Uses SerpAPI to find internship listings across multiple keywords (e.g., "Software Engineering Internship", "Backend Developer Internship").
- **Smart Email Discovery**:
  - **Strategy A**: Scrapes the job listing page for contact emails.
  - **Strategy B**: If no email is found, performs a targeted search for the company's "Careers" or "Contact" page to find the right point of contact.
  - **Domain Verification**: Validates emails against the company's domain to ensure accuracy and safety.
- **AI-Powered Personalization**: Uses OpenAI (GPT-4o-mini) to generate unique, context-aware emails based on the job description and your resume.
- **Automated Mailing**: Sends emails via SMTP (Gmail) with your resume attached.
- **Safety & Control**:
  - **Rate Limiting**: Configurable daily limits to prevent spamming.
  - **Domain Filtering**: Whitelists/Blacklists to avoid recruiting agencies or spam.
  - **Logging**: Tracks every sent email in `data/sent_log.csv` to avoid duplicates.

## 🛠️ Prerequisites

- **Python 3.10+**
- **API Keys**:
  - [SerpAPI](https://serpapi.com/) (for Google Search results)
  - [OpenAI API](https://platform.openai.com/) (for email generation)
- **Gmail Account**: An App Password is required for SMTP access.

## 📦 Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/internship-ai-agent.git
    cd internship-ai-agent
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up Environment Variables**:
    Create a `.env` file in the root directory and add your credentials:
    ```env
    SERPAPI_KEY=your_serpapi_key_here
    OPENAI_API_KEY=your_openai_api_key_here
    GMAIL_USER=your_email@gmail.com
    GMAIL_APP_PASSWORD=your_gmail_app_password
    ```

4.  **Prepare your Data**:
    - Place your resume PDF at `data/resume.pdf`.
    - (Optional) Review `config/config.yaml` to customize search keywords and email templates.

## ⚙️ Configuration

The behavior of the agent is controlled by `config/config.yaml`. You can customize:

- **Search Keywords**: List of roles you are looking for.
- **Locations**: Target countries or "Remote".
- **Email Template**: The base structure for the AI to fill in.
- **Rate Limits**: Max emails per day.

## 🚀 Usage

Run the agent using the following command:

```bash
python -m src.main
```

The agent will:
1.  Search for jobs based on your keywords.
2.  Filter out previously applied companies.
3.  Attempt to find a valid contact email.
4.  Generate a personalized email.
5.  Send the application with your resume attached.
6.  Log the result in `data/sent_log.csv`.

## 📂 Project Structure

```
internship_ai_agent/
├── config/
│   └── config.yaml       # Main configuration file
├── data/
│   ├── resume.pdf        # Your resume (Input)
│   └── sent_log.csv      # Log of sent applications (Output)
├── logs/                 # Application logs
├── src/
│   ├── main.py           # Entry point and orchestration
│   ├── search_agent.py   # Handles job searching via SerpAPI
│   ├── parser.py         # Web scraping and email extraction
│   ├── email_agent.py    # AI email generation
│   ├── mailer.py         # SMTP email sending
│   └── utils.py          # Helper functions (PDF text, logging)
├── .env                  # Secrets (Not committed)
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## ⚠️ Disclaimer

This tool is intended for personal use to assist in the job application process. Please use it responsibly.
- **Do not spam.** Respect rate limits and company policies.
- **Verify emails.** While the agent tries to be accurate, always double-check who you are sending data to.
- **Review generated emails.** AI can make mistakes; it's recommended to review the logs or run in a "dry run" mode first if you are unsure.