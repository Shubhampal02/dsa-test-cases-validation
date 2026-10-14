from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

from database import Base


class ValidationResult(Base):

    __tablename__ = "validation_results"

    id = Column(Integer, primary_key=True)

    test_case_id = Column(String, nullable=False)

    question_id = Column(String, nullable=False)

    input_data = Column(Text, nullable=False)

    expected_output = Column(Text, nullable=False)

    status = Column(String, nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )