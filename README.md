# Email Classification and Automation System

## Project Overview

This is an intelligent email processing system that uses Large Language Models (LLMs) to automatically classify and respond to incoming emails. The system can categorize emails into different types and generate appropriate responses.

## Folder Structure

```
email-classifier/
│
├── config/
│   └── settings.py        # Configuration settings
│
├── data/
│   ├── sample_emails.csv  # Sample email dataset
│   └── few_shot_examples.csv  # Training examples for classification
│
├── logs/                  # Application logs
│
├── prompts/
│   ├── builder.py         # Prompt generation logic
│   └── templates.py       # Prompt templates and examples
│
├── src/
│   ├── core/
│   │   ├── models.py      # Data models and enums
│   │   └── processor.py   # Email processing logic
│   │
│   ├── handlers/
│   │   └── email_handlers.py  # Different email handling strategies
│   │
│   └── utils/
│       └── logger.py      # Logging configuration
│
├── tests/                 # (Future) Unit and integration tests
│
├── .env                   # Environment variables (not tracked in git)
├── main.py                # Main application entry point
├── requirements.txt       # Project dependencies
└── README.md              # Project documentation
```

## Prerequisites

- Python 3.8+
- OpenAI API Key

## Setup

1. Clone the repository
2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your OpenAI API key
```
OPENAI_API_KEY=your_openai_api_key_here
```

## Data Preparation

### Email Data
Place your email dataset in `data/sample_emails.csv`. The CSV should have the following columns:
- `id`: Unique identifier for the email
- `from`: Sender's email address
- `subject`: Email subject
- `body`: Email content
- `timestamp`: Timestamp of the email

Example structure:
```csv
id,from,subject,body,timestamp
001,customer@example.com,Product Issue,"Details of the email...",2024-03-15T10:30:00Z
```

### Few-Shot Examples
The `data/few_shot_examples.csv` contains training examples for email classification. It should have two columns:
- `text`: Example email text
- `category`: Corresponding classification (complaint, inquiry, feedback, support_request, other)

## Usage

Run the main application:
```bash
python main.py
```

This will:
1. Load sample emails from `data/sample_emails.csv`
2. Classify each email
3. Generate appropriate responses
4. Print processing results

## Email Categories

The system supports five email categories:
- `complaint`: Negative feedback or issue reports
- `inquiry`: Questions or requests for information
- `feedback`: Positive or neutral comments
- `support_request`: Technical help or support needs
- `other`: Emails that don't fit other categories

## Customization

You can customize:
- Classification categories in `src/core/models.py`
- Prompt templates in `prompts/templates.py`
- Response generation logic in `src/core/processor.py`
- Email handling strategies in `src/handlers/email_handlers.py`

## Logging

Logs are generated in the `logs/` directory:
- Console output
- Detailed log file (`app.log`)

## Configuration

Key configuration parameters are in `config/settings.py`:
- OpenAI API key
- Model name
- Classification temperature
- Retry attempts

## Future Improvements

- Add more robust error handling
- Implement more sophisticated few-shot learning
- Create comprehensive test suite
- Add support for multiple LLM providers

## Troubleshooting

- Ensure `.env` file is correctly configured
- Check internet connection
- Verify OpenAI API key permissions
- Review logs in `logs/app.log` for detailed error information

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request