from typing import Dict
import logging
from src.core.models import EmailCategory
from src.core.processor import EmailProcessor

logger = logging.getLogger(__name__)

class BaseEmailHandler:
    def __init__(self, processor: EmailProcessor):
        self.processor = processor

    def handle(self, email: Dict, category: EmailCategory) -> Dict:
        response = {
            "response": self.processor.generate_response(email, category.value),
            "email_id": email["id"],
            "category": category.value,
        }
        return response

class ComplaintHandler(BaseEmailHandler):
    def handle(self, email: Dict, category: EmailCategory) -> Dict:
        response = super().handle(email, category)
        logger.info(f"Creating urgent ticket for complaint {email['id']}")
        return response

class InquiryHandler(BaseEmailHandler):
    pass

class FeedbackHandler(BaseEmailHandler):
    def handle(self, email: Dict, category: EmailCategory) -> Dict:
        response = super().handle(email, category)
        logger.info(f"Logging feedback for {email['id']}")
        return response

class SupportHandler(BaseEmailHandler):
    def handle(self, email: Dict, category: EmailCategory) -> Dict:
        response = super().handle(email, category)
        logger.info(f"Creating support ticket for {email['id']}")
        return response

class OtherHandler(BaseEmailHandler):
    pass

class HandlerFactory:
    handlers = {
        EmailCategory.COMPLAINT: ComplaintHandler,
        EmailCategory.INQUIRY: InquiryHandler,
        EmailCategory.FEEDBACK: FeedbackHandler,
        EmailCategory.SUPPORT_REQUEST: SupportHandler,
        EmailCategory.OTHER: OtherHandler
    }

    @classmethod
    def get_handler(cls, category: EmailCategory, processor: EmailProcessor):
        handler_class = cls.handlers.get(category, OtherHandler)
        return handler_class(processor)