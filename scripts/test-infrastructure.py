#!/usr/bin/env python3
"""
Infrastructure Smoke Test for DSRS Development Environment
Tests connectivity to all infrastructure services before deploying application services.
"""

import sys
import time
import psycopg2
import pymongo
import redis
from kafka import KafkaProducer, KafkaConsumer
import json
from datetime import datetime

def test_postgresql():
    """Test PostgreSQL connection and basic operations."""
    print("🔍 Testing PostgreSQL...")
    try:
        conn = psycopg2.connect(
            host="127.0.0.1",
            port=5432,
            database="dsrs_dev",
            user="dev",
            password="dev123"
        )
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT COUNT(*) FROM households;")
        count = cursor.fetchone()[0]
        print(f"  ✅ PostgreSQL connected successfully")
        print(f"  ✅ Found {count} sample households")
        
        # Test table structure
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' ORDER BY table_name;
        """)
        tables = [row[0] for row in cursor.fetchall()]
        expected_tables = ['eligibility_assessments', 'event_outbox', 'household_members', 'households', 'payment_records']
        
        if all(table in tables for table in expected_tables):
            print(f"  ✅ All required tables present: {', '.join(tables)}")
        else:
            print(f"  ⚠️  Missing tables. Found: {', '.join(tables)}")
            
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"  ❌ PostgreSQL test failed: {e}")
        return False

def test_mongodb():
    """Test MongoDB connection and basic operations."""
    print("🔍 Testing MongoDB...")
    try:
        client = pymongo.MongoClient(
            "mongodb://dev:dev123@localhost:27017/dsrs_analytics?authSource=admin"
        )
        
        # Test connection
        client.admin.command('ping')
        print(f"  ✅ MongoDB connected successfully")
        
        # Test database and collections
        db = client.dsrs_analytics
        collections = db.list_collection_names()
        expected_collections = ['household_metrics', 'eligibility_metrics', 'payment_metrics', 'system_metrics']
        
        if all(col in collections for col in expected_collections):
            print(f"  ✅ All required collections present: {', '.join(collections)}")
        else:
            print(f"  ⚠️  Missing collections. Found: {', '.join(collections)}")
        
        # Test sample data
        sample_count = db.household_metrics.count_documents({})
        print(f"  ✅ Found {sample_count} sample metrics")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"  ❌ MongoDB test failed: {e}")
        return False

def test_redis():
    """Test Redis connection and basic operations."""
    print("🔍 Testing Redis...")
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        # Test connection
        r.ping()
        print(f"  ✅ Redis connected successfully")
        
        # Test basic operations
        test_key = f"test_key_{int(time.time())}"
        r.set(test_key, "test_value", ex=60)  # Expire in 60 seconds
        value = r.get(test_key)
        
        if value == "test_value":
            print(f"  ✅ Redis read/write operations working")
        else:
            print(f"  ⚠️  Redis read/write test failed")
            
        r.delete(test_key)
        return True
        
    except Exception as e:
        print(f"  ❌ Redis test failed: {e}")
        return False

def test_kafka():
    """Test Kafka (Redpanda) connection and basic operations."""
    print("🔍 Testing Kafka (Redpanda)...")
    try:
        # Test producer
        producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        test_topic = f"test_topic_{int(time.time())}"
        test_message = {
            "test": True,
            "timestamp": datetime.now().isoformat(),
            "message": "Infrastructure test message"
        }
        
        # Send test message
        future = producer.send(test_topic, test_message)
        producer.flush()
        print(f"  ✅ Kafka producer working")
        
        # Test consumer
        consumer = KafkaConsumer(
            test_topic,
            bootstrap_servers=['localhost:9092'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            consumer_timeout_ms=5000,
            auto_offset_reset='earliest'
        )
        
        messages_received = 0
        for message in consumer:
            if message.value.get('test') == True:
                messages_received += 1
                break
                
        if messages_received > 0:
            print(f"  ✅ Kafka consumer working")
        else:
            print(f"  ⚠️  Kafka consumer test failed")
            
        consumer.close()
        producer.close()
        return True
        
    except Exception as e:
        print(f"  ❌ Kafka test failed: {e}")
        return False

def main():
    """Run all infrastructure tests."""
    print("🚀 DSRS Infrastructure Smoke Test")
    print("=" * 50)
    
    tests = [
        ("PostgreSQL", test_postgresql),
        ("MongoDB", test_mongodb),
        ("Redis", test_redis),
        ("Kafka", test_kafka)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print()
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"  ❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    print()
    print("📊 Test Results Summary")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name:<15} {status}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 All infrastructure tests passed! Ready to deploy application services.")
        return 0
    else:
        print("⚠️  Some infrastructure tests failed. Please fix issues before deploying applications.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
