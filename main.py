from src.utils.logger import setup_logging
from src.core.automation_system import EmailAutomationSystem
import pandas as pd
import logging


logger = logging.getLogger(__name__)


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