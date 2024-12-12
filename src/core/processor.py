import logging
import re
import time
from typing import Dict, Optional
from openai import OpenAI
from config.settings import OPENAI_API_KEY, MODEL_NAME, MAX_RETRIES, TEMPERATURE
from src.core.models import EmailCategory, PromptTemplate
from prompts.builder import EmailPromptBuilder

logger = logging.getLogger(__name__)

class EmailProcessor:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.prompt_builder = EmailPromptBuilder()
        self.template = PromptTemplate(
            system_message="You are an expert email classifier. Always classify emails into exactly one category.",
            examples=self.prompt_builder.examples,
            output_format=self.prompt_builder.output_format
        )
        self.valid_categories = EmailCategory.list_values()

    def classify_email(self, email: Dict) -> Optional[EmailCategory]:
        prompt = self.prompt_builder.build_prompt(email)
        
        for attempt in range(MAX_RETRIES):
            try:
                completion = self.client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": self.template.system_message},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=TEMPERATURE
                )

                response = completion.choices[0].message.content.strip().lower()
                logger.debug(f"Raw response: {response}")
                
                classification = self._parse_classification(response)
                if classification:
                    return classification
                    
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == MAX_RETRIES - 1:
                    raise
                time.sleep(1)
                
        return None

    def _parse_classification(self, response: str) -> Optional[EmailCategory]:
        try:
            classification_match = re.search(r"classification:\s*([a-z_]+)", response, re.MULTILINE)
            confidence_match = re.search(r"confidence:\s*([a-z]+)", response, re.MULTILINE)
            
            if classification_match and confidence_match:
                classification = classification_match.group(1).strip()
                confidence = confidence_match.group(1).strip()
                
                if classification in self.valid_categories:
                    logger.info(f"Classification: {classification} (Confidence: {confidence})")
                    return EmailCategory.from_string(classification)
                else:
                    logger.warning(f"Invalid classification received: {classification}")
                    
        except Exception as e:
            logger.error(f"Parse error: {e}, Response: {response}")
            
        return None

    def generate_response(self, email: Dict, classification: str) -> str:
        prompt = f"Write a professional response to the following email based on the classification: {classification}\n\n{email['body']}"
        
        completion = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a customer service agent responding to an email"},
                {"role": "user", "content": prompt}
            ],
            temperature=TEMPERATURE
        )
        
        response = completion.choices[0].message.content
        if not response:
            raise ValueError("Failed to generate response")
            
        return response