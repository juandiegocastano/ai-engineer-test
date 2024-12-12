import logging
from src.utils.logger import setup_logging
import pandas as pd
from src.core.models import Example, EmailCategory

logger = logging.getLogger(__name__)

def load_examples_from_csv(filepath: str = "data/few_shot_examples.csv") -> list[Example]:
    """Load examples from CSV file and convert to Example objects."""
    try:
        df = pd.read_csv(filepath)
        examples = []
        for _, row in df.iterrows():
            category = EmailCategory.from_string(row['category'])
            if category:
                examples.append(Example(row['text'], category))
            else:
                logger.warning(f"Invalid category in CSV: {row['category']}")
        return examples
    except Exception as e:
        logger.error(f"Failed to load examples from CSV: {e}")
        # Fallback to default examples if CSV loading fails
        return DEFAULT_FALLBACK_EXAMPLES

# Fallback examples in case CSV loading fails
DEFAULT_FALLBACK_EXAMPLES = [
    Example("Your product is broken and I want a refund", EmailCategory.COMPLAINT),
    Example("What are your business hours?", EmailCategory.INQUIRY),
    Example("Great service, thank you!", EmailCategory.FEEDBACK),
    Example("I need help installing the software", EmailCategory.SUPPORT_REQUEST)
]

# Load examples from CSV file
DEFAULT_EXAMPLES = load_examples_from_csv()

SYSTEM_MESSAGE = "You are an expert email classifier. Always classify emails into exactly one category."

OUTPUT_FORMAT = """
Provide your answer in this format:
Classification: [category]
Confidence: [high/medium/low]
"""