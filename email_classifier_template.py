# Configuration and imports
import os
import json
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime
import logging
import re
import time
import logging
from enum import Enum
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Sample email dataset
sample_emails = [
    {
        "id": "001",
        "from": "angry.customer@example.com",
        "subject": "Broken product received",
        "body": "I received my order #12345 yesterday but it arrived completely damaged. This is unacceptable and I demand a refund immediately. This is the worst customer service I've experienced.",
        "timestamp": "2024-03-15T10:30:00Z"
    },
    {
        "id": "002",
        "from": "curious.shopper@example.com",
        "subject": "Question about product specifications",
        "body": "Hi, I'm interested in buying your premium package but I couldn't find information about whether it's compatible with Mac OS. Could you please clarify this? Thanks!",
        "timestamp": "2024-03-15T11:45:00Z"
    },
    {
        "id": "003",
        "from": "happy.user@example.com",
        "subject": "Amazing customer support",
        "body": "I just wanted to say thank you for the excellent support I received from Sarah on your team. She went above and beyond to help resolve my issue. Keep up the great work!",
        "timestamp": "2024-03-15T13:15:00Z"
    },
    {
        "id": "004",
        "from": "tech.user@example.com",
        "subject": "Need help with installation",
        "body": "I've been trying to install the software for the past hour but keep getting error code 5123. I've already tried restarting my computer and clearing the cache. Please help!",
        "timestamp": "2024-03-15T14:20:00Z"
    },
    {
        "id": "005",
        "from": "business.client@example.com",
        "subject": "Partnership opportunity",
        "body": "Our company is interested in exploring potential partnership opportunities with your organization. Would it be possible to schedule a call next week to discuss this further?",
        "timestamp": "2024-03-15T15:00:00Z"
    }
]

class EmailCategory(Enum):
    COMPLAINT = "complaint"
    INQUIRY = "inquiry"
    FEEDBACK = "feedback"
    SUPPORT_REQUEST = "support_request"
    OTHER = "other"
    
    @classmethod
    def from_string(cls, category: str) -> Optional['EmailCategory']:
        """Convert string to enum value safely"""
        try:
            return cls(category.lower())
        except ValueError:
            return None
    
    @classmethod
    def list_values(cls) -> set:
        """Get all valid category values"""
        return {category.value for category in cls}

@dataclass
class Example:
    text: str
    category: EmailCategory

@dataclass
class PromptTemplate:
    system_message: str
    examples: List[Example]
    output_format: str
    temperature: float = 0.3

class EmailPromptBuilder:
    def __init__(self):
        self.examples = [
            Example(
                "Your product is broken and I want a refund",
                EmailCategory.COMPLAINT
            ),
            Example(
                "What are your business hours?",
                EmailCategory.INQUIRY
            ),
            Example(
                "Great service, thank you!",
                EmailCategory.FEEDBACK
            ),
            Example(
                "I need help installing the software",
                EmailCategory.SUPPORT_REQUEST
            )
        ]
        
        self.output_format = """
        Provide your answer in this format:
        Classification: [category]
        Confidence: [high/medium/low]
        """
        
    def build_prompt(self, email: Dict) -> str:
        examples_text = self._format_examples()
        return f"""
        Classify the following email into exactly one of these categories: {', '.join(EmailCategory.list_values())}.

        {examples_text}

        Now classify this email:
        Subject: {email['subject']}
        Body: {email['body']}

        {self.output_format}
        """

    def _format_examples(self) -> str:
        return "\n".join([
            f"{i+1}. Email: \"{example.text}\"\n"
            f"Classification: {example.category.value}"
            for i, example in enumerate(self.examples)
        ])


class EmailProcessor:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.prompt_builder = EmailPromptBuilder()
        self.template = PromptTemplate(
            system_message="You are an expert email classifier. Always classify emails into exactly one category.",
            examples=self.prompt_builder.examples,
            output_format=self.prompt_builder.output_format
        )
        self.valid_categories = EmailCategory.list_values()

    def classify_email(self, email: Dict) -> Optional[EmailCategory]:
        prompt = self.prompt_builder.build_prompt(email)
        
        num_retry = 3
        for attempt in range(num_retry):
            try:
                completion = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": self.template.system_message},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )

                response = completion.choices[0].message.content.strip().lower()
                logger.debug(f"Raw response: {response}")
                
                # Updated regex patterns to handle multiline responses
                classification_pattern = r"classification:\s*([a-z_]+)"
                confidence_pattern = r"confidence:\s*([a-z]+)"
                
                try:
                    classification_match = re.search(classification_pattern, response, re.MULTILINE)
                    confidence_match = re.search(confidence_pattern, response, re.MULTILINE)
                    
                    if classification_match and confidence_match:
                        classification = classification_match.group(1).strip()
                        confidence = confidence_match.group(1).strip()
                        
                        # Now valid_categories will be available
                        if classification in self.valid_categories:
                            logger.info(f"Classification: {classification} (Confidence: {confidence})")
                            return EmailCategory.from_string(classification)
                        else:
                            logger.warning(f"Invalid classification received: {classification}")
                    else:
                        logger.error(f"Failed to parse response: {response}")
                        
                except AttributeError as ae:
                    logger.error(f"Parse error: {ae}, Response: {response}")
                    continue
                    
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == num_retry - 1:
                    raise ValueError(f"Failed to classify email after {num_retry} attempts: {e}")
                time.sleep(1)
                
        return None
                
        

    def generate_response(self, email: Dict, classification: str) -> Optional[str]:
        """
        Generate an automated response based on email classification.
        
        TODO:
        1. Design the response generation prompt
        2. Implement appropriate response templates
        3. Add error handling
        """
        # 1. Design and implement the classification prompt 
        # TODO: make the classes dynamic
        prompt = f"Write a professional response to the following email based on the classification: {classification}\n\n {email['body']}"
        completion = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an agent responding to an email"},
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # print(completion.choices[0].message) 
        response_email = completion.choices[0].message.content
        # print(response_email )
        if response_email:
            return response_email 
        else: 
            raise ValueError("Failed to generate response")
        
         
class EmailAutomationSystem:
    def __init__(self, processor: EmailProcessor):
        """Initialize the automation system with an EmailProcessor."""
        self.processor = processor
        self.response_handlers = {
            "complaint": self._handle_complaint,
            "inquiry": self._handle_inquiry,
            "feedback": self._handle_feedback,
            "support_request": self._handle_support_request,
            "other": self._handle_other
        }

    def process_email(self, email: Dict) -> Dict:
        """
        Process a single email through the complete pipeline.
        Returns a dictionary with the processing results.
        
        TODO:
        1. Implement the complete processing pipeline
        2. Add appropriate error handling
        3. Return processing results
        """
        predicted_class = self.processor.classify_email(email) 
        handler = self.response_handlers.get(predicted_class.value) 
        if handler:
            return handler(email, predicted_class)
        else:
            raise ValueError(f"Invalid email classification: {predicted_class}")

    def _handle_complaint(self, email: Dict, predicted_class: EmailCategory):
        """
        Handle complaint emails.
        TODO: Implement complaint handling logic
        """
        
        # return send_complaint_response(email, self.processor.generate_response(email, "complaint"))
        response = {
            "response": self.processor.generate_response(email, predicted_class.value),
            "email_id": email["id"],
            "category": predicted_class.value,
        }
        return response

    def _handle_inquiry(self, email: Dict, predicted_class: EmailCategory):
        """
        Handle inquiry emails.
        TODO: Implement inquiry handling logic
        """
        # return send_complaint_response(email, self.processor.generate_response(email, "inquiry"))
        response = {
            "response": self.processor.generate_response(email, predicted_class.value),
            "email_id": email["id"],
            "category": predicted_class.value,
        }
        return response

    def _handle_feedback(self, email: Dict, predicted_class: EmailCategory):
        """
        Handle feedback emails.
        TODO: Implement feedback handling logic
        """
        # return send_complaint_response(email, self.processor.generate_response(email, "feedback"))
        response = {
            "response": self.processor.generate_response(email, predicted_class.value),
            "email_id": email["id"],
            "category": predicted_class.value,
        }
        return response

    def _handle_support_request(self, email: Dict, predicted_class: EmailCategory):
        """
        Handle support request emails.
        TODO: Implement support request handling logic
        """
        # return send_complaint_response(email, self.processor.generate_response(email, "support_request"))
        response = {
            "response": self.processor.generate_response(email, predicted_class.value),
            "email_id": email["id"],
            "category": predicted_class.value,
        }
        return response

    def _handle_other(self, email: Dict, predicted_class: EmailCategory):
        """
        Handle other category emails.
        TODO: Implement handling logic for other categories
        """
        # return send_complaint_response(email, self.processor.generate_response(email, "other"))
        response = {
            "response": self.processor.generate_response(email, predicted_class.value),
            "email_id": email["id"],
            "category": predicted_class.value,
        }
        return response

# Mock service functions
def send_complaint_response(email_id: str, response: str):
    """Mock function to simulate sending a response to a complaint"""
    logger.info(f"Sending complaint response for email {email_id}")
    # In real implementation: integrate with email service


def send_standard_response(email_id: str, response: str):
    """Mock function to simulate sending a standard response"""
    logger.info(f"Sending standard response for email {email_id}")
    # In real implementation: integrate with email service


def create_urgent_ticket(email_id: str, category: str, context: str):
    """Mock function to simulate creating an urgent ticket"""
    logger.info(f"Creating urgent ticket for email {email_id}")
    # In real implementation: integrate with ticket system


def create_support_ticket(email_id: str, context: str):
    """Mock function to simulate creating a support ticket"""
    logger.info(f"Creating support ticket for email {email_id}")
    # In real implementation: integrate with ticket system


def log_customer_feedback(email_id: str, feedback: str):
    """Mock function to simulate logging customer feedback"""
    logger.info(f"Logging feedback for email {email_id}")
    # In real implementation: integrate with feedback system


def run_demonstration():
    """Run a demonstration of the complete system."""
    # Initialize the system
    processor = EmailProcessor()
    automation_system = EmailAutomationSystem(processor)

    # Process all sample emails
    results = [] 
    for email in sample_emails:
        logger.info(f"\nProcessing email {email['id']}...")
        result = automation_system.process_email(email)
        results.append(result)

    # Create a summary DataFrame 
    df = pd.DataFrame(data=results)

    return df


# Example usage:
if __name__ == "__main__":
    results_df = run_demonstration() 
    print(results_df)
