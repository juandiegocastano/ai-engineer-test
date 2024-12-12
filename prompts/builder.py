from typing import Dict, List
import csv
from src.core.models import Example, EmailCategory
from .templates import DEFAULT_EXAMPLES, OUTPUT_FORMAT

class EmailPromptBuilder:
    def __init__(self, examples: List[Example] = None):
        self.examples = examples or DEFAULT_EXAMPLES
        self.output_format = OUTPUT_FORMAT

    def build_prompt(self, email: Dict) -> str:
        examples_text = self._format_examples()
        return f"""
        Classify the following email into exactly one of these categories: {', '.join(EmailCategory.list_values())}.

        For reference, here are some examples of email categories:
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