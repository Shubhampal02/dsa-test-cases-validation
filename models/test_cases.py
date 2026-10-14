from sqlalchemy import Column, Integer, String, Text

from database import Base

class TestCase(Base):

    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True)

    question_id = Column(String, nullable=False)

    test_case_id = Column(String, nullable=False)

    category = Column(String, nullable=False)

    description = Column(String, nullable=False)

    input_data = Column(Text, nullable=False)