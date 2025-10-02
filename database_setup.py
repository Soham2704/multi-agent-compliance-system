import sqlalchemy
from sqlalchemy import create_engine, Column, String, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# --- 1. Database Configuration ---
DB_NAME = "rules.db"
DB_PATH = os.path.join("rules_db", DB_NAME)
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Create the directory if it doesn't exist
os.makedirs("rules_db", exist_ok=True)

# --- 2. SQLAlchemy Setup ---
# The engine is the connection to our database file
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# A session is how we will interact with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the blueprint for our table classes
Base = declarative_base()


# --- 3. Define the Table Schema as a Python Class ---
# This class is our "universal translator" for the 'rules' table.
class Rule(Base):
    __tablename__ = "rules"

    id = Column(String, primary_key=True, index=True)
    city = Column(String, index=True)
    rule_type = Column(String, index=True)
    conditions = Column(JSON)
    entitlements = Column(JSON)
    notes = Column(Text)


# --- 4. Main Execution Block to Create the Database ---
def create_database():
    """
    This function creates the database and the 'rules' table if they don't exist.
    """
    print(f"--- Creating database at '{DB_PATH}' ---")
    Base.metadata.create_all(bind=engine)
    print("--- Database and 'rules' table created successfully. ---")


if __name__ == "__main__":
    create_database()