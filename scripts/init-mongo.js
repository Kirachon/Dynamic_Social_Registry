// Initialize MongoDB for DSRS Analytics Service
// This script sets up the analytics database with initial collections and indexes

// Switch to the analytics database
db = db.getSiblingDB('dsrs_analytics');

// Create collections for analytics data
db.createCollection('household_metrics');
db.createCollection('eligibility_metrics');
db.createCollection('payment_metrics');
db.createCollection('system_metrics');

// Create indexes for better query performance
db.household_metrics.createIndex({ "timestamp": 1 });
db.household_metrics.createIndex({ "household_id": 1 });
db.household_metrics.createIndex({ "metric_type": 1, "timestamp": 1 });

db.eligibility_metrics.createIndex({ "timestamp": 1 });
db.eligibility_metrics.createIndex({ "household_id": 1 });
db.eligibility_metrics.createIndex({ "eligibility_status": 1, "timestamp": 1 });

db.payment_metrics.createIndex({ "timestamp": 1 });
db.payment_metrics.createIndex({ "household_id": 1 });
db.payment_metrics.createIndex({ "payment_status": 1, "timestamp": 1 });

db.system_metrics.createIndex({ "timestamp": 1 });
db.system_metrics.createIndex({ "service_name": 1, "timestamp": 1 });
db.system_metrics.createIndex({ "metric_name": 1, "timestamp": 1 });

// Insert sample analytics data for development
var sampleHouseholdMetrics = [
    {
        household_id: "550e8400-e29b-41d4-a716-446655440001",
        metric_type: "registration",
        value: 1,
        timestamp: new Date(),
        metadata: {
            source: "registry_service",
            household_size: 4,
            monthly_income: 2500.00
        }
    },
    {
        household_id: "550e8400-e29b-41d4-a716-446655440002",
        metric_type: "registration",
        value: 1,
        timestamp: new Date(Date.now() - 86400000), // 1 day ago
        metadata: {
            source: "registry_service",
            household_size: 2,
            monthly_income: 1800.00
        }
    }
];

var sampleEligibilityMetrics = [
    {
        household_id: "550e8400-e29b-41d4-a716-446655440001",
        eligibility_status: "eligible",
        eligibility_score: 85.5,
        assessment_date: new Date(),
        timestamp: new Date(),
        metadata: {
            source: "eligibility_service",
            criteria_met: ["income_threshold", "household_size", "documentation"]
        }
    },
    {
        household_id: "550e8400-e29b-41d4-a716-446655440002",
        eligibility_status: "pending",
        eligibility_score: 72.0,
        assessment_date: new Date(Date.now() - 3600000), // 1 hour ago
        timestamp: new Date(Date.now() - 3600000),
        metadata: {
            source: "eligibility_service",
            criteria_met: ["income_threshold", "household_size"],
            criteria_pending: ["documentation"]
        }
    }
];

var samplePaymentMetrics = [
    {
        household_id: "550e8400-e29b-41d4-a716-446655440001",
        payment_amount: 500.00,
        payment_status: "completed",
        payment_date: new Date(),
        timestamp: new Date(),
        metadata: {
            source: "payment_service",
            payment_method: "bank_transfer",
            transaction_reference: "TXN-2025-001"
        }
    }
];

var sampleSystemMetrics = [
    {
        service_name: "registry_service",
        metric_name: "requests_per_minute",
        value: 45,
        timestamp: new Date(),
        metadata: {
            endpoint: "/api/v1/households",
            method: "POST"
        }
    },
    {
        service_name: "eligibility_service",
        metric_name: "assessment_processing_time",
        value: 1250, // milliseconds
        timestamp: new Date(),
        metadata: {
            endpoint: "/api/v1/assessments",
            method: "POST"
        }
    },
    {
        service_name: "payment_service",
        metric_name: "payment_success_rate",
        value: 98.5, // percentage
        timestamp: new Date(),
        metadata: {
            payment_method: "bank_transfer",
            period: "last_24_hours"
        }
    }
];

// Insert sample data
try {
    db.household_metrics.insertMany(sampleHouseholdMetrics);
    print("✅ Inserted sample household metrics");
} catch (e) {
    print("⚠️  Error inserting household metrics: " + e);
}

try {
    db.eligibility_metrics.insertMany(sampleEligibilityMetrics);
    print("✅ Inserted sample eligibility metrics");
} catch (e) {
    print("⚠️  Error inserting eligibility metrics: " + e);
}

try {
    db.payment_metrics.insertMany(samplePaymentMetrics);
    print("✅ Inserted sample payment metrics");
} catch (e) {
    print("⚠️  Error inserting payment metrics: " + e);
}

try {
    db.system_metrics.insertMany(sampleSystemMetrics);
    print("✅ Inserted sample system metrics");
} catch (e) {
    print("⚠️  Error inserting system metrics: " + e);
}

// Create a user for the analytics service
try {
    db.createUser({
        user: "analytics_service",
        pwd: "dev123",
        roles: [
            { role: "readWrite", db: "dsrs_analytics" }
        ]
    });
    print("✅ Created analytics service user");
} catch (e) {
    print("⚠️  Error creating user (may already exist): " + e);
}

// Create aggregation views for common queries
db.createView("daily_registrations", "household_metrics", [
    {
        $match: {
            metric_type: "registration"
        }
    },
    {
        $group: {
            _id: {
                $dateToString: {
                    format: "%Y-%m-%d",
                    date: "$timestamp"
                }
            },
            count: { $sum: "$value" },
            total_households: { $sum: 1 }
        }
    },
    {
        $sort: { "_id": -1 }
    }
]);

db.createView("eligibility_summary", "eligibility_metrics", [
    {
        $group: {
            _id: "$eligibility_status",
            count: { $sum: 1 },
            avg_score: { $avg: "$eligibility_score" }
        }
    }
]);

db.createView("payment_summary", "payment_metrics", [
    {
        $group: {
            _id: "$payment_status",
            count: { $sum: 1 },
            total_amount: { $sum: "$payment_amount" },
            avg_amount: { $avg: "$payment_amount" }
        }
    }
]);

print("🎉 MongoDB analytics database initialized successfully!");
print("📊 Collections created: household_metrics, eligibility_metrics, payment_metrics, system_metrics");
print("🔍 Views created: daily_registrations, eligibility_summary, payment_summary");
print("👤 User created: analytics_service");
print("📈 Sample data inserted for development testing");
