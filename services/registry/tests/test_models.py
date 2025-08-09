import pytest
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

from app.models import Household
from app.db import Base


@pytest.fixture(scope="session")
def postgres_container():
    """Start a PostgreSQL container for testing"""
    with PostgresContainer("postgres:15-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def test_engine(postgres_container):
    """Create a test database engine"""
    connection_url = postgres_container.get_connection_url()
    engine = create_engine(connection_url)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def test_session(test_engine):
    """Create a test database session"""
    Session = sessionmaker(bind=test_engine)
    session = Session()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


class TestHouseholdModel:
    """Test cases for the Household model"""
    
    def test_create_household(self, test_session):
        """Test creating a household with all fields"""
        household = Household(
            head_of_household_name="John Doe",
            address="123 Main St, Manila",
            phone_number="+63912345678",
            email="john.doe@example.com",
            household_size=4,
            monthly_income=25000.50
        )
        
        test_session.add(household)
        test_session.commit()
        
        # Verify the household was created
        assert household.id is not None
        assert isinstance(household.id, uuid.UUID)
        assert household.head_of_household_name == "John Doe"
        assert household.address == "123 Main St, Manila"
        assert household.phone_number == "+63912345678"
        assert household.email == "john.doe@example.com"
        assert household.household_size == 4
        assert float(household.monthly_income) == 25000.50
        assert household.created_at is not None
        assert household.updated_at is not None
    
    def test_create_household_minimal_fields(self, test_session):
        """Test creating a household with only required fields"""
        household = Household(
            head_of_household_name="Jane Smith",
            address="456 Oak Ave, Quezon City"
        )
        
        test_session.add(household)
        test_session.commit()
        
        # Verify the household was created with defaults
        assert household.id is not None
        assert household.head_of_household_name == "Jane Smith"
        assert household.address == "456 Oak Ave, Quezon City"
        assert household.phone_number is None
        assert household.email is None
        assert household.household_size == 1  # Default value
        assert household.monthly_income is None
        assert household.created_at is not None
        assert household.updated_at is not None
    
    def test_household_string_length_validation(self, test_session):
        """Test that string fields respect length constraints"""
        # Test head_of_household_name max length (255)
        long_name = "A" * 256
        household = Household(
            head_of_household_name=long_name,
            address="Test Address"
        )
        
        test_session.add(household)
        
        # This should raise an exception due to length constraint
        with pytest.raises(Exception):
            test_session.commit()
    
    def test_household_phone_validation(self, test_session):
        """Test phone number field validation"""
        household = Household(
            head_of_household_name="Test User",
            address="Test Address",
            phone_number="A" * 21  # Exceeds 20 character limit
        )
        
        test_session.add(household)
        
        # This should raise an exception due to length constraint
        with pytest.raises(Exception):
            test_session.commit()
    
    def test_household_email_validation(self, test_session):
        """Test email field validation"""
        household = Household(
            head_of_household_name="Test User",
            address="Test Address",
            email="A" * 256  # Exceeds 255 character limit
        )
        
        test_session.add(household)
        
        # This should raise an exception due to length constraint
        with pytest.raises(Exception):
            test_session.commit()
    
    def test_household_query_operations(self, test_session):
        """Test querying households"""
        # Create test households
        household1 = Household(
            head_of_household_name="Alice Johnson",
            address="789 Pine St, Makati",
            monthly_income=15000.00
        )
        household2 = Household(
            head_of_household_name="Bob Wilson",
            address="321 Elm St, Pasig",
            monthly_income=35000.00
        )
        
        test_session.add_all([household1, household2])
        test_session.commit()
        
        # Test query by name
        result = test_session.query(Household).filter(
            Household.head_of_household_name == "Alice Johnson"
        ).first()
        assert result is not None
        assert result.head_of_household_name == "Alice Johnson"
        
        # Test query by income range
        low_income_households = test_session.query(Household).filter(
            Household.monthly_income <= 20000
        ).all()
        assert len(low_income_households) == 1
        assert low_income_households[0].head_of_household_name == "Alice Johnson"
        
        # Test count
        total_households = test_session.query(Household).count()
        assert total_households == 2
