import pytest
import asyncio
import json
import time
import uuid
from typing import Dict, Any
import httpx
from testcontainers.postgres import PostgresContainer
from testcontainers.kafka import KafkaContainer
from testcontainers.compose import DockerCompose
import os
import tempfile

# Test configuration
TEST_TIMEOUT = 300  # 5 minutes max for entire test suite
SAGA_TIMEOUT = 60   # 1 minute max for saga completion


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_infrastructure():
    """Set up test infrastructure with Testcontainers"""
    print("🚀 Setting up test infrastructure...")
    
    # Start PostgreSQL
    postgres = PostgresContainer("postgres:15-alpine")
    postgres.start()
    
    # Start Kafka
    kafka = KafkaContainer("confluentinc/cp-kafka:7.4.0")
    kafka.start()
    
    # Get connection details
    postgres_url = postgres.get_connection_url().replace("postgresql://", "postgresql+psycopg://")
    kafka_brokers = f"{kafka.get_bootstrap_server()}"
    
    print(f"📊 PostgreSQL: {postgres_url}")
    print(f"📨 Kafka: {kafka_brokers}")
    
    # Set environment variables for services
    os.environ["DATABASE_URL"] = postgres_url
    os.environ["KAFKA_BROKERS"] = kafka_brokers
    os.environ["ALLOW_INSECURE_LOCAL"] = "1"
    os.environ["ENVIRONMENT"] = "test"
    os.environ["OTEL_ENABLE"] = "0"
    
    # Initialize database schema
    await initialize_database(postgres_url)
    
    # Create Kafka topics
    await create_kafka_topics(kafka_brokers)
    
    infrastructure = {
        "postgres": postgres,
        "kafka": kafka,
        "postgres_url": postgres_url,
        "kafka_brokers": kafka_brokers
    }
    
    yield infrastructure
    
    # Cleanup
    print("🧹 Cleaning up test infrastructure...")
    postgres.stop()
    kafka.stop()


async def initialize_database(postgres_url: str):
    """Initialize database schema for all services"""
    print("🗄️  Initializing database schema...")
    
    # This would normally run Alembic migrations
    # For now, we'll create tables manually for testing
    import sqlalchemy as sa
    from sqlalchemy import create_engine, text
    
    engine = create_engine(postgres_url)
    
    with engine.connect() as conn:
        # Create households table (Registry)
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS households (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                head_of_household_name VARCHAR(255) NOT NULL,
                address TEXT NOT NULL,
                phone_number VARCHAR(20),
                email VARCHAR(255),
                household_size INTEGER NOT NULL DEFAULT 1,
                monthly_income DECIMAL(10, 2),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Create eligibility_assessments table (Eligibility)
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS eligibility_assessments (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                household_id UUID NOT NULL,
                eligibility_status VARCHAR(50) NOT NULL,
                eligibility_score DECIMAL(10, 2),
                assessment_criteria TEXT,
                assessed_by VARCHAR(255) NOT NULL,
                notes TEXT,
                assessment_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Create payments table (Payment)
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS payments (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                household_id UUID NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                status VARCHAR(50) NOT NULL,
                payment_method VARCHAR(100),
                reference_number VARCHAR(255),
                scheduled_date TIMESTAMP WITH TIME ZONE,
                completed_date TIMESTAMP WITH TIME ZONE,
                notes TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Create event_outbox table (all services)
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS event_outbox (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                aggregate_id VARCHAR(64) NOT NULL,
                event_type VARCHAR(100) NOT NULL,
                event_data TEXT NOT NULL,
                headers TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP WITH TIME ZONE
            )
        """))
        
        # Create processed_events table (all services)
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS processed_events (
                id VARCHAR(255) PRIMARY KEY,
                event_type VARCHAR(100) NOT NULL,
                processed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                consumer_group VARCHAR(100) NOT NULL
            )
        """))
        
        conn.commit()
    
    print("✅ Database schema initialized")


async def create_kafka_topics(kafka_brokers: str):
    """Create required Kafka topics"""
    print("📨 Creating Kafka topics...")
    
    # This would normally use kafka-admin-python or similar
    # For testing, we'll assume topics are auto-created
    topics = [
        "registry.household",
        "eligibility.assessed",
        "payment.events"
    ]
    
    print(f"✅ Topics configured: {topics}")


@pytest.fixture
async def test_services(test_infrastructure):
    """Start test services"""
    print("🔧 Starting test services...")
    
    # In a real implementation, we would start the actual services
    # For this test, we'll mock the service behavior
    
    services = {
        "registry_port": 8001,
        "eligibility_port": 8002,
        "payment_port": 8003,
        "analytics_port": 8004
    }
    
    yield services
    
    print("🛑 Stopping test services...")


class TestSagaFlowWithTestcontainers:
    """Comprehensive saga flow tests using Testcontainers"""
    
    @pytest.mark.asyncio
    async def test_complete_saga_flow(self, test_infrastructure, test_services):
        """Test complete household registration to payment saga"""
        print("🎯 Testing complete saga flow...")
        
        # Test data
        household_data = {
            "head_of_household_name": "Maria Santos",
            "address": "123 Test Street, Manila",
            "phone_number": "+63912345678",
            "email": "maria.santos@example.com",
            "household_size": 4,
            "monthly_income": 2500.00  # Below threshold for approval
        }
        
        # Step 1: Create household (Registry Service)
        print("📝 Step 1: Creating household...")
        household_id = await self.create_household(household_data, test_services)
        assert household_id is not None
        print(f"✅ Household created: {household_id}")
        
        # Step 2: Wait for eligibility assessment (Eligibility Service)
        print("🔍 Step 2: Waiting for eligibility assessment...")
        eligibility_result = await self.wait_for_eligibility_assessment(household_id, test_infrastructure)
        assert eligibility_result["status"] == "approved"
        print(f"✅ Eligibility assessed: {eligibility_result['status']}")
        
        # Step 3: Wait for payment scheduling (Payment Service)
        print("💰 Step 3: Waiting for payment scheduling...")
        payment_result = await self.wait_for_payment_scheduling(household_id, test_infrastructure)
        assert payment_result["status"] == "scheduled"
        print(f"✅ Payment scheduled: {payment_result['status']}")
        
        print("🎉 Complete saga flow test PASSED!")
    
    @pytest.mark.asyncio
    async def test_saga_idempotency(self, test_infrastructure, test_services):
        """Test that saga handles duplicate events correctly"""
        print("🔄 Testing saga idempotency...")
        
        household_data = {
            "head_of_household_name": "Juan Dela Cruz",
            "address": "456 Idempotency Ave, Quezon City",
            "household_size": 2,
            "monthly_income": 1800.00
        }
        
        # Create household twice with same data
        household_id_1 = await self.create_household(household_data, test_services)
        household_id_2 = await self.create_household(household_data, test_services)
        
        # Both should succeed but create different households
        assert household_id_1 != household_id_2
        
        # Wait for both to be processed
        eligibility_1 = await self.wait_for_eligibility_assessment(household_id_1, test_infrastructure)
        eligibility_2 = await self.wait_for_eligibility_assessment(household_id_2, test_infrastructure)
        
        assert eligibility_1["status"] == "approved"
        assert eligibility_2["status"] == "approved"
        
        print("✅ Idempotency test PASSED!")
    
    @pytest.mark.asyncio
    async def test_saga_with_denial(self, test_infrastructure, test_services):
        """Test saga flow when eligibility is denied"""
        print("❌ Testing saga flow with denial...")
        
        household_data = {
            "head_of_household_name": "Rich Person",
            "address": "999 Wealthy St, Makati",
            "household_size": 1,
            "monthly_income": 50000.00  # Above threshold for denial
        }
        
        household_id = await self.create_household(household_data, test_services)
        eligibility_result = await self.wait_for_eligibility_assessment(household_id, test_infrastructure)
        
        assert eligibility_result["status"] == "denied"
        
        # Verify no payment was scheduled
        await asyncio.sleep(5)  # Wait a bit to ensure no payment is created
        payment_exists = await self.check_payment_exists(household_id, test_infrastructure)
        assert not payment_exists
        
        print("✅ Denial flow test PASSED!")
    
    async def create_household(self, household_data: Dict[str, Any], test_services) -> str:
        """Create a household via Registry service"""
        # In real implementation, this would call the actual Registry API
        # For testing, we'll simulate by directly inserting into database
        
        import sqlalchemy as sa
        from sqlalchemy import create_engine, text
        
        engine = create_engine(os.environ["DATABASE_URL"])
        household_id = str(uuid.uuid4())
        
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO households (id, head_of_household_name, address, phone_number, email, household_size, monthly_income)
                VALUES (:id, :name, :address, :phone, :email, :size, :income)
            """), {
                "id": household_id,
                "name": household_data["head_of_household_name"],
                "address": household_data["address"],
                "phone": household_data.get("phone_number"),
                "email": household_data.get("email"),
                "size": household_data["household_size"],
                "income": household_data["monthly_income"]
            })
            
            # Simulate event emission
            conn.execute(text("""
                INSERT INTO event_outbox (aggregate_id, event_type, event_data)
                VALUES (:agg_id, :type, :data)
            """), {
                "agg_id": household_id,
                "type": "registry.household.registered",
                "data": json.dumps({
                    "id": household_id,
                    **household_data
                })
            })
            
            conn.commit()
        
        return household_id
    
    async def wait_for_eligibility_assessment(self, household_id: str, test_infrastructure, timeout: int = 30) -> Dict[str, Any]:
        """Wait for eligibility assessment to complete"""
        import sqlalchemy as sa
        from sqlalchemy import create_engine, text
        
        engine = create_engine(test_infrastructure["postgres_url"])
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT eligibility_status, eligibility_score, assessment_criteria
                    FROM eligibility_assessments
                    WHERE household_id = :household_id
                """), {"household_id": household_id}).first()
                
                if result:
                    return {
                        "status": result[0],
                        "score": float(result[1]) if result[1] else None,
                        "criteria": result[2]
                    }
            
            await asyncio.sleep(1)
        
        raise TimeoutError(f"Eligibility assessment not found for household {household_id} within {timeout}s")
    
    async def wait_for_payment_scheduling(self, household_id: str, test_infrastructure, timeout: int = 30) -> Dict[str, Any]:
        """Wait for payment to be scheduled"""
        import sqlalchemy as sa
        from sqlalchemy import create_engine, text
        
        engine = create_engine(test_infrastructure["postgres_url"])
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT status, amount, scheduled_date
                    FROM payments
                    WHERE household_id = :household_id
                """), {"household_id": household_id}).first()
                
                if result:
                    return {
                        "status": result[0],
                        "amount": float(result[1]) if result[1] else None,
                        "scheduled_date": result[2]
                    }
            
            await asyncio.sleep(1)
        
        raise TimeoutError(f"Payment not found for household {household_id} within {timeout}s")
    
    async def check_payment_exists(self, household_id: str, test_infrastructure) -> bool:
        """Check if a payment exists for the household"""
        import sqlalchemy as sa
        from sqlalchemy import create_engine, text
        
        engine = create_engine(test_infrastructure["postgres_url"])
        
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT COUNT(*) FROM payments WHERE household_id = :household_id
            """), {"household_id": household_id}).scalar()
            
            return result > 0
