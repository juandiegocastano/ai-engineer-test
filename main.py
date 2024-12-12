from src.utils.logger import setup_logging
from src.core.processor import EmailProcessor
from src.handlers.email_handlers import HandlerFactory
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class EmailAutomationSystem:
    def __init__(self):
        self.processor = EmailProcessor()

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

def run_demonstration():
    setup_logging()
    system = EmailAutomationSystem()
    
    # Load sample emails from CSV
    df = pd.read_csv('data/sample_emails.csv')
    emails = df.to_dict('records')
    
    results = []
    for email in emails:
        logger.info(f"Processing email {email['id']}...")
        result = system.process_email(email)
        results.append(result)
    
    results_df = pd.DataFrame(results)
    print("\nResults:")
    print(results_df)
    return results_df

if __name__ == "__main__":
    run_demonstration()