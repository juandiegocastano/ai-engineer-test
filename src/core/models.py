from enum import Enum
from dataclasses import dataclass
from typing import Optional, List

class EmailCategory(Enum):
    COMPLAINT = "complaint"
    INQUIRY = "inquiry"
    FEEDBACK = "feedback"
    SUPPORT_REQUEST = "support_request"
    OTHER = "other"

    @classmethod
    def from_string(cls, category: str) -> Optional['EmailCategory']:
        try:
            return cls(category.lower())
        except ValueError:
            return None

    @classmethod
    def list_values(cls) -> set:
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