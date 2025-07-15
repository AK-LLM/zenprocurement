"""
Script to set up test users for the AI Procurement Platform
Run this after setting up the database to create test accounts
"""

import os
from supabase import create_client, Client
import hashlib
from datetime import datetime

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_test_users():
    """Create test users for the platform"""
    
    test_users = [
        {
            "username": "admin",
            "email": "admin@procurement.ai",
            "password": "hello",  # Simple password for testing
            "is_admin": True,
            "subscription_tier": "enterprise"
        },
        {
            "username": "testuser1",
            "email": "testuser1@example.com", 
            "password": "hello",
            "is_admin": False,
            "subscription_tier": "basic"
        },
        {
            "username": "testuser2",
            "email": "testuser2@example.com",
            "password": "hello", 
            "is_admin": False,
            "subscription_tier": "premium"
        },
        {
            "username": "testuser3",
            "email": "testuser3@example.com",
            "password": "hello",
            "is_admin": False,
            "subscription_tier": "enterprise"
        },
        {
            "username": "banking_demo",
            "email": "banking@demo.com",
            "password": "demo123",
            "is_admin": False,
            "subscription_tier": "premium"
        },
        {
            "username": "f1_demo", 
            "email": "f1@demo.com",
            "password": "demo123",
            "is_admin": False,
            "subscription_tier": "enterprise"
        },
        {
            "username": "shipping_demo",
            "email": "shipping@demo.com", 
            "password": "demo123",
            "is_admin": False,
            "subscription_tier": "premium"
        }
    ]
    
    print("Creating test users...")
    
    for user_data in test_users:
        try:
            # Check if user already exists
            existing = supabase.table("users").select("*").eq("username", user_data["username"]).execute()
            
            if existing.data:
                print(f"User {user_data['username']} already exists, skipping...")
                continue
            
            # Create user
            user_record = {
                "username": user_data["username"],
                "email": user_data["email"],
                "password_hash": hash_password(user_data["password"]),
                "is_admin": user_data["is_admin"],
                "subscription_tier": user_data["subscription_tier"],
                "subscription_status": "active",
                "created_at": datetime.now().isoformat(),
                "profile_data": {
                    "demo_account": True,
                    "industry": "Demo" if "demo" in user_data["username"] else "General"
                }
            }
            
            result = supabase.table("users").insert(user_record).execute()
            print(f"✅ Created user: {user_data['username']} ({user_data['subscription_tier']})")
            
        except Exception as e:
            print(f"❌ Error creating user {user_data['username']}: {str(e)}")
    
    print("\n🎉 Test user setup complete!")
    print("\n📋 Test Account Credentials:")
    print("=" * 50)
    for user in test_users:
        role = "ADMIN" if user["is_admin"] else "USER"
        print(f"{user['username']:15} | {user['password']:10} | {user['subscription_tier']:10} | {role}")
    print("=" * 50)

def create_sample_data():
    """Create sample data for testing"""
    print("\nCreating sample data...")
    
    # Sample feedback
    sample_feedback = [
        {
            "user_id": "testuser1",  # This would need to be actual UUID in production
            "feedback_text": "Great platform! Love the AI suggestions.",
            "rating": 5,
            "category": "general",
            "created_at": datetime.now().isoformat()
        },
        {
            "user_id": "testuser2",
            "feedback_text": "The product sourcing feature is very helpful.",
            "rating": 4,
            "category": "feature",
            "created_at": datetime.now().isoformat()
        }
    ]
    
    # Note: In production, you'd need to get actual user IDs
    print("Sample data creation would require actual user IDs from the database.")
    print("Run the application first, then manually create sample data through the UI.")

if __name__ == "__main__":
    create_test_users()
    create_sample_data()