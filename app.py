import streamlit as st
from supabase import create_client, Client
import os
from datetime import datetime
from auth import authenticate_user, create_user, initiate_password_reset, reset_password, check_subscription_limits, log_user_activity
from admin_dashboard import admin_dashboard
from product_sourcing import enhanced_product_sourcing
from ai_suggestions import industry_ai_suggestions
from custom_branding import branding_manager
from social_trends import trend_monitor
from order_management import order_manager
from analytics import user_analytics
import hashlib

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# Page setup
st.set_page_config(
    page_title="AI Procurement Platform", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .subscription-badge {
        background: #28a745;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Check for password reset token in URL
    query_params = st.experimental_get_query_params()
    if "reset_token" in query_params:
        handle_password_reset(query_params["reset_token"][0])
        return
    
    # Authentication check
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        show_login_page()
    else:
        show_main_app()

def show_login_page():
    """Display login/registration page"""
    st.markdown('<div class="main-header"><h1>🚀 AI Procurement Platform</h1><p>Your intelligent procurement solution</p></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Login", "Register", "Forgot Password"])
    
    with tab1:
        st.subheader("Login to Your Account")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login", type="primary"):
                if username and password:
                    success, user_data, message = authenticate_user(username, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user = user_data
                        log_user_activity(user_data["id"], "login")
                        st.success("Login successful!")
                        st.experimental_rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please enter both username and password")
        
        with col2:
            st.info("**Test Accounts:**\n\n**Admin:** admin / hello\n\n**User:** testuser1 / hello")
    
    with tab2:
        st.subheader("Create New Account")
        new_username = st.text_input("Choose Username", key="reg_username")
        new_email = st.text_input("Email Address", key="reg_email")
        new_password = st.text_input("Password", type="password", key="reg_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
        
        subscription_tier = st.selectbox(
            "Choose Subscription Plan",
            ["basic", "premium", "enterprise"],
            format_func=lambda x: {
                "basic": "Basic - $29.99/month (10 searches/day)",
                "premium": "Premium - $99.99/month (100 searches/day)",
                "enterprise": "Enterprise - $299.99/month (Unlimited)"
            }[x]
        )
        
        if st.button("Create Account", type="primary"):
            if all([new_username, new_email, new_password, confirm_password]):
                if new_password == confirm_password:
                    success, message = create_user(new_username, new_email, new_password, subscription_tier)
                    if success:
                        st.success("Account created successfully! Please login.")
                    else:
                        st.error(message)
                else:
                    st.error("Passwords do not match")
            else:
                st.error("Please fill in all fields")
    
    with tab3:
        st.subheader("Reset Password")
        reset_email = st.text_input("Enter your email address", key="reset_email")
        
        if st.button("Send Reset Link"):
            if reset_email:
                success, message = initiate_password_reset(reset_email)
                if success:
                    st.success("Password reset email sent! Check your inbox.")
                else:
                    st.error(message)
            else:
                st.error("Please enter your email address")

def handle_password_reset(reset_token):
    """Handle password reset with token"""
    st.subheader("Reset Your Password")
    
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm New Password", type="password")
    
    if st.button("Reset Password"):
        if new_password and confirm_password:
            if new_password == confirm_password:
                success, message = reset_password(reset_token, new_password)
                if success:
                    st.success("Password reset successfully! You can now login.")
                    st.experimental_set_query_params()  # Clear URL params
                else:
                    st.error(message)
            else:
                st.error("Passwords do not match")
        else:
            st.error("Please enter both password fields")

def show_main_app():
    """Main application interface"""
    user = st.session_state.user
    
    # Header with user info
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown(f'<div class="main-header"><h2>Welcome, {user["username"]}!</h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<span class="subscription-badge">{user["subscription_tier"].upper()}</span>', unsafe_allow_html=True)
    with col3:
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.experimental_rerun()
    
    # Sidebar navigation
    if user.get("is_admin"):
        pages = ["Dashboard", "Product Sourcing", "AI Suggestions", "Custom Branding", "Social Trends", "Order Management", "Analytics", "Admin Panel"]
    else:
        pages = ["Dashboard", "Product Sourcing", "AI Suggestions", "Custom Branding", "Order Management", "My Analytics"]
    
    page = st.sidebar.selectbox("Navigation", pages)
    
    # Subscription limits info
    with st.sidebar:
        st.markdown("---")
        st.subheader("Subscription Limits")
        limits = get_subscription_limits(user["subscription_tier"])
        for action, limit in limits.items():
            if limit == -1:
                st.write(f"• {action}: Unlimited")
            else:
                usage = get_daily_usage(user["id"], action)
                st.write(f"• {action}: {usage}/{limit}")
    
    # Route to appropriate page
    if page == "Dashboard":
        show_dashboard()
    elif page == "Product Sourcing":
        enhanced_product_sourcing()
    elif page == "AI Suggestions":
        industry_ai_suggestions()
    elif page == "Custom Branding":
        branding_manager()
    elif page == "Social Trends":
        trend_monitor()
    elif page == "Order Management":
        order_manager()
    elif page == "Analytics" or page == "My Analytics":
        user_analytics()
    elif page == "Admin Panel" and user.get("is_admin"):
        admin_dashboard()

def show_dashboard():
    """User dashboard with key metrics"""
    user = st.session_state.user
    
    st.title("📊 Dashboard")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Get user statistics
    searches_today = get_daily_usage(user["id"], "search")
    suggestions_today = get_daily_usage(user["id"], "ai_suggestion")
    orders_total = get_user_orders_count(user["id"])
    last_activity = get_last_activity(user["id"])
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Searches Today", searches_today)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("AI Suggestions", suggestions_today)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Orders", orders_total)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Account Age", f"{(datetime.now() - datetime.fromisoformat(user['created_at'].replace('Z', '+00:00'))).days} days")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Recent activity
    st.subheader("Recent Activity")
    recent_activities = get_recent_activities(user["id"])
    
    if recent_activities:
        for activity in recent_activities[:10]:
            with st.expander(f"{activity['action_type'].title()} - {activity['created_at'][:10]}"):
                st.json(activity.get('details', {}))
    else:
        st.info("No recent activity found. Start exploring the platform!")
    
    # Quick actions
    st.subheader("Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 Start Product Search", use_container_width=True):
            st.session_state.page = "Product Sourcing"
            st.experimental_rerun()
    
    with col2:
        if st.button("🤖 Get AI Suggestions", use_container_width=True):
            st.session_state.page = "AI Suggestions"
            st.experimental_rerun()
    
    with col3:
        if st.button("🎨 Manage Branding", use_container_width=True):
            st.session_state.page = "Custom Branding"
            st.experimental_rerun()

# Helper functions
def get_subscription_limits(tier):
    """Get subscription limits for tier"""
    limits = {
        "basic": {
            "searches": 10,
            "ai_suggestions": 5,
            "image_generations": 3,
            "quotes": 5
        },
        "premium": {
            "searches": 100,
            "ai_suggestions": 50,
            "image_generations": 25,
            "quotes": 50
        },
        "enterprise": {
            "searches": -1,
            "ai_suggestions": -1,
            "image_generations": -1,
            "quotes": -1
        }
    }
    return limits.get(tier, limits["basic"])

def get_daily_usage(user_id, action_type):
    """Get daily usage count for user action"""
    today = datetime.now().date().isoformat()
    try:
        result = supabase.table("user_activity").select("*").eq("user_id", user_id).eq("action_type", action_type).gte("created_at", today).execute()
        return len(result.data) if result.data else 0
    except:
        return 0

def get_user_orders_count(user_id):
    """Get total orders count for user"""
    try:
        result = supabase.table("orders").select("*").eq("user_id", user_id).execute()
        return len(result.data) if result.data else 0
    except:
        return 0

def get_last_activity(user_id):
    """Get user's last activity"""
    try:
        result = supabase.table("user_activity").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(1).execute()
        return result.data[0] if result.data else None
    except:
        return None

def get_recent_activities(user_id):
    """Get recent user activities"""
    try:
        result = supabase.table("user_activity").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(20).execute()
        return result.data if result.data else []
    except:
        return []

if __name__ == "__main__":
    main()