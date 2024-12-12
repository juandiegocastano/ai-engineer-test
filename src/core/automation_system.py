from src.utils.logger import setup_logging 
from src.core.processor import EmailProcessor
from src.handlers.email_handlers import HandlerFactory 
import pandas as pd
import logging 


logger = logging.getLogger(__name__) 


class EmailAutomationSystem:
    def __init__(self, processor=None):
        """Initialize with optional processor for testing"""
        self.processor = processor or EmailProcessor()

    def process_email(self, email: dict) -> dict:
        try:
            category = self.processor.classify_email(email)
            if not category:
                logger.warning(f"Could not classify email {email['id']}")
                return {"email_id": email["id"], "error": "Classification failed"}

            handler = HandlerFactory.get_handler(category, self.processor)
            return handler.handle(email, category)

        except Exception as e:
            logger.error(f"Error processing email {email['id']}: {str(e)}")
            return {"email_id": email["id"], "error": str(e)}