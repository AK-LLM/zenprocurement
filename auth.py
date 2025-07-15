import streamlit as st
import hashlib
import secrets
from supabase import create_client, Client
import os
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed

def generate_reset_token() -> str:
    """Generate secure reset token"""
    return secrets.token_urlsafe(32)

def send_reset_email(email: str, reset_token: str):
    """Send password reset email"""
    try:
        smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        smtp_username = os.environ.get("SMTP_USERNAME")
        smtp_password = os.environ.get("SMTP_PASSWORD")
        
        if not all([smtp_username, smtp_password]):
            st.error("Email configuration not set up")
            return False
            
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = email
        msg['Subject'] = "Password Reset - AI Procurement Platform"
        
        reset_link = f"http://localhost:8501/?reset_token={reset_token}"
        body = f"""
        Hello,
        
        You requested a password reset for your AI Procurement Platform account.
        
        Click the link below to reset your password:
        {reset_link}
        
        This link will expire in 1 hour.
        
        If you didn't request this reset, please ignore this email.
        
        Best regards,
        AI Procurement Platform Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        return False

def create_user(username: str, email: str, password: str, subscription_tier: str = "basic") -> bool:
    """Create new user account"""
    try:
        # Check if user already exists
        existing_user = supabase.table("users").select("*").eq("username", username).execute()
        if existing_user.data:
            return False, "Username already exists"
            
        existing_email = supabase.table("users").select("*").eq("email", email).execute()
        if existing_email.data:
            return False, "Email already registered"
        
        # Create user
        user_data = {
            "username": username,
            "email": email,
            "password_hash": hash_password(password),
            "subscription_tier": subscription_tier,
            "subscription_status": "active",
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "is_admin": False
        }
        
        result = supabase.table("users").insert(user_data).execute()
        return True, "Account created successfully"
        
    except Exception as e:
        return False, f"Error creating account: {str(e)}"

def authenticate_user(username: str, password: str) -> tuple:
    """Authenticate user login"""
    try:
        user = supabase.table("users").select("*").eq("username", username).execute()
        
        if not user.data:
            return False, None, "Invalid username or password"
            
        user_data = user.data[0]
        
        if not verify_password(password, user_data["password_hash"]):
            return False, None, "Invalid username or password"
            
        if user_data["subscription_status"] != "active":
            return False, None, "Account suspended or inactive"
        
        # Update last login
        supabase.table("users").update({
            "last_login": datetime.now().isoformat()
        }).eq("id", user_data["id"]).execute()
        
        return True, user_data, "Login successful"
        
    except Exception as e:
        return False, None, f"Login error: {str(e)}"

def initiate_password_reset(email: str) -> bool:
    """Initiate password reset process"""
    try:
        user = supabase.table("users").select("*").eq("email", email).execute()
        
        if not user.data:
            return False, "Email not found"
            
        reset_token = generate_reset_token()
        expires_at = (datetime.now() + timedelta(hours=1)).isoformat()
        
        # Store reset token
        supabase.table("password_resets").insert({
            "user_id": user.data[0]["id"],
            "reset_token": reset_token,
            "expires_at": expires_at,
            "used": False,
            "created_at": datetime.now().isoformat()
        }).execute()
        
        # Send reset email
        if send_reset_email(email, reset_token):
            return True, "Reset email sent successfully"
        else:
            return False, "Failed to send reset email"
            
    except Exception as e:
        return False, f"Reset error: {str(e)}"

def reset_password(reset_token: str, new_password: str) -> tuple:
    """Reset password using token"""
    try:
        # Verify token
        reset_data = supabase.table("password_resets").select("*").eq("reset_token", reset_token).eq("used", False).execute()
        
        if not reset_data.data:
            return False, "Invalid or expired reset token"
            
        reset_record = reset_data.data[0]
        
        # Check if token expired
        if datetime.fromisoformat(reset_record["expires_at"]) < datetime.now():
            return False, "Reset token has expired"
        
        # Update password
        supabase.table("users").update({
            "password_hash": hash_password(new_password)
        }).eq("id", reset_record["user_id"]).execute()
        
        # Mark token as used
        supabase.table("password_resets").update({
            "used": True
        }).eq("id", reset_record["id"]).execute()
        
        return True, "Password reset successfully"
        
    except Exception as e:
        return False, f"Reset error: {str(e)}"

def get_user_subscription_info(user_id: int) -> dict:
    """Get user subscription details"""
    try:
        user = supabase.table("users").select("*").eq("id", user_id).execute()
        if user.data:
            return user.data[0]
        return None
    except Exception as e:
        st.error(f"Error fetching subscription info: {str(e)}")
        return None

def check_subscription_limits(user_id: int, action_type: str) -> bool:
    """Check if user can perform action based on subscription tier"""
    user_info = get_user_subscription_info(user_id)
    if not user_info:
        return False
        
    tier = user_info.get("subscription_tier", "basic")
    
    # Define limits per tier
    limits = {
        "basic": {
            "searches_per_day": 10,
            "ai_suggestions_per_day": 5,
            "image_generations_per_day": 3,
            "quotes_per_day": 5
        },
        "premium": {
            "searches_per_day": 100,
            "ai_suggestions_per_day": 50,
            "image_generations_per_day": 25,
            "quotes_per_day": 50
        },
        "enterprise": {
            "searches_per_day": -1,  # Unlimited
            "ai_suggestions_per_day": -1,
            "image_generations_per_day": -1,
            "quotes_per_day": -1
        }
    }
    
    if tier not in limits:
        return False
        
    tier_limits = limits[tier]
    daily_limit = tier_limits.get(f"{action_type}_per_day", 0)
    
    if daily_limit == -1:  # Unlimited
        return True
        
    # Check today's usage
    today = datetime.now().date().isoformat()
    usage = supabase.table("user_activity").select("*").eq("user_id", user_id).eq("action_type", action_type).gte("created_at", today).execute()
    
    return len(usage.data) < daily_limit

def log_user_activity(user_id: int, action_type: str, details: dict = None):
    """Log user activity for analytics"""
    try:
        activity_data = {
            "user_id": user_id,
            "action_type": action_type,
            "details": details or {},
            "created_at": datetime.now().isoformat()
        }
        
        supabase.table("user_activity").insert(activity_data).execute()
    except Exception as e:
        st.error(f"Error logging activity: {str(e)}")