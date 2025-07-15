import streamlit as st
import pandas as pd
from supabase import create_client, Client
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from collections import defaultdict

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

def admin_dashboard():
    """Admin dashboard for platform management"""
    if not st.session_state.get("user") or not st.session_state.user.get("is_admin"):
        st.error("🚫 Access denied. Admin privileges required.")
        return
    
    st.title("🔧 Admin Dashboard")
    st.markdown("---")
    
    # Admin navigation
    admin_page = st.sidebar.selectbox(
        "Admin Functions",
        ["📊 Overview", "👥 User Management", "📈 Analytics", "💳 Subscriptions", "📋 Reports", "🛡️ Moderation"]
    )
    
    if admin_page == "📊 Overview":
        show_admin_overview()
    elif admin_page == "👥 User Management":
        show_user_management()
    elif admin_page == "📈 Analytics":
        show_analytics_dashboard()
    elif admin_page == "💳 Subscriptions":
        show_subscription_management()
    elif admin_page == "📋 Reports":
        show_system_reports()
    elif admin_page == "🛡️ Moderation":
        show_content_moderation()

def show_admin_overview():
    """Show admin overview dashboard"""
    st.header("Platform Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Get metrics
    users = supabase.table("users").select("*").execute()
    total_users = len(users.data) if users.data else 0
    
    thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
    active_users = supabase.table("users").select("*").gte("last_login", thirty_days_ago).execute()
    active_count = len(active_users.data) if active_users.data else 0
    
    today = datetime.now().date().isoformat()
    today_activities = supabase.table("user_activity").select("*").gte("created_at", today).execute()
    today_activity_count = len(today_activities.data) if today_activities.data else 0
    
    revenue = calculate_monthly_revenue()
    
    with col1:
        st.metric("👥 Total Users", total_users, delta=f"+{get_new_users_today()}")
    with col2:
        st.metric("🟢 Active Users (30d)", active_count, delta=f"{(active_count/total_users*100):.1f}%" if total_users > 0 else "0%")
    with col3:
        st.metric("⚡ Today's Activities", today_activity_count)
    with col4:
        st.metric("💰 Monthly Revenue", f"${revenue:,.2f}")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Activity Trends (Last 7 Days)")
        show_activity_chart()
    
    with col2:
        st.subheader("User Registration Trend")
        show_registration_trend()
    
    # Subscription distribution
    st.subheader("Subscription Distribution")
    show_subscription_pie_chart()
    
    # Recent user activities
    st.subheader("Recent Platform Activities")
    show_recent_activities()

def show_user_management():
    """User management interface"""
    st.header("User Management")
    
    # Search and filters
    col1, col2, col3 = st.columns(3)
    with col1:
        search_term = st.text_input("🔍 Search users", placeholder="Username or email...")
    with col2:
        filter_tier = st.selectbox("Filter by subscription", ["All", "basic", "premium", "enterprise"])
    with col3:
        filter_status = st.selectbox("Filter by status", ["All", "active", "inactive", "suspended"])
    
    # Get users with filters
    users_query = supabase.table("users").select("*")
    
    if search_term:
        # Note: This is a simplified search - in production, use proper text search
        users = supabase.table("users").select("*").execute()
        if users.data:
            filtered_users = [
                u for u in users.data 
                if search_term.lower() in u.get('username', '').lower() or 
                   search_term.lower() in u.get('email', '').lower()
            ]
        else:
            filtered_users = []
    else:
        users = users_query.execute()
        filtered_users = users.data if users.data else []
    
    # Apply additional filters
    if filter_tier != "All":
        filtered_users = [u for u in filtered_users if u.get('subscription_tier') == filter_tier]
    if filter_status != "All":
        filtered_users = [u for u in filtered_users if u.get('subscription_status') == filter_status]
    
    if filtered_users:
        # Convert to DataFrame
        df = pd.DataFrame(filtered_users)
        df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d')
        df['last_login'] = pd.to_datetime(df['last_login']).dt.strftime('%Y-%m-%d %H:%M')
        
        # Display users table
        st.dataframe(
            df[['username', 'email', 'subscription_tier', 'subscription_status', 'created_at', 'last_login', 'is_admin']],
            use_container_width=True
        )
        
        # User management actions
        st.subheader("User Actions")
        
        if filtered_users:
            selected_user_index = st.selectbox(
                "Select user for actions", 
                range(len(filtered_users)),
                format_func=lambda i: f"{filtered_users[i]['username']} ({filtered_users[i]['email']})"
            )
            
            selected_user = filtered_users[selected_user_index]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("🚫 Suspend User"):
                    update_user_status(selected_user['id'], 'suspended')
                    st.success("User suspended")
                    st.experimental_rerun()
            
            with col2:
                if st.button("✅ Activate User"):
                    update_user_status(selected_user['id'], 'active')
                    st.success("User activated")
                    st.experimental_rerun()
            
            with col3:
                new_tier = st.selectbox("Change subscription", ["basic", "premium", "enterprise"])
                if st.button("💳 Update Subscription"):
                    update_user_subscription(selected_user['id'], new_tier)
                    st.success(f"Subscription updated to {new_tier}")
                    st.experimental_rerun()
            
            with col4:
                if st.button("👑 Toggle Admin"):
                    toggle_admin_status(selected_user['id'], not selected_user['is_admin'])
                    st.success("Admin status toggled")
                    st.experimental_rerun()
            
            # User details
            with st.expander("User Details"):
                st.json(selected_user)
    else:
        st.info("No users found matching the criteria.")

def show_analytics_dashboard():
    """Analytics and reporting dashboard"""
    st.header("Analytics Dashboard")
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", datetime.now())
    
    # User behavior analytics
    activities = supabase.table("user_activity").select("*").gte("created_at", start_date.isoformat()).lte("created_at", end_date.isoformat()).execute()
    
    if activities.data:
        df_activities = pd.DataFrame(activities.data)
        
        # Activity distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Activity Type Distribution")
            activity_counts = df_activities['action_type'].value_counts()
            fig_pie = px.pie(values=activity_counts.values, names=activity_counts.index)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.subheader("Daily Activity Trend")
            df_activities['date'] = pd.to_datetime(df_activities['created_at']).dt.date
            daily_activities = df_activities.groupby('date').size().reset_index(name='count')
            fig_line = px.line(daily_activities, x='date', y='count')
            st.plotly_chart(fig_line, use_container_width=True)
        
        # Top users by activity
        st.subheader("Most Active Users")
        user_activity = df_activities['user_id'].value_counts().head(10)
        
        user_details = []
        for user_id, count in user_activity.items():
            user = supabase.table("users").select("username, email, subscription_tier").eq("id", user_id).execute()
            if user.data:
                user_details.append({
                    "Username": user.data[0]['username'],
                    "Email": user.data[0]['email'],
                    "Subscription": user.data[0]['subscription_tier'],
                    "Activity Count": count
                })
        
        if user_details:
            st.dataframe(pd.DataFrame(user_details), use_container_width=True)
        
        # Buying behavior analysis
        st.subheader("User Buying Behavior")
        show_buying_behavior_analysis(start_date, end_date)
    else:
        st.info("No activity data found for the selected date range.")

def show_subscription_management():
    """Subscription management interface"""
    st.header("Subscription Management")
    
    # Subscription metrics
    users = supabase.table("users").select("subscription_tier, subscription_status").execute()
    
    if users.data:
        df_subs = pd.DataFrame(users.data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Subscription Tiers")
            tier_counts = df_subs['subscription_tier'].value_counts()
            fig_bar = px.bar(x=tier_counts.index, y=tier_counts.values, 
                           title="Users by Subscription Tier")
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            st.subheader("Subscription Status")
            status_counts = df_subs['subscription_status'].value_counts()
            fig_pie = px.pie(values=status_counts.values, names=status_counts.index)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # Revenue analysis
        st.subheader("Revenue Analysis")
        monthly_revenue = calculate_monthly_revenue()
        projected_annual = monthly_revenue * 12
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Monthly Revenue", f"${monthly_revenue:,.2f}")
        with col2:
            st.metric("Projected Annual Revenue", f"${projected_annual:,.2f}")
        with col3:
            avg_revenue_per_user = monthly_revenue / len(users.data) if users.data else 0
            st.metric("Average Revenue Per User", f"${avg_revenue_per_user:.2f}")

def show_system_reports():
    """System reports and exports"""
    st.header("System Reports")
    
    report_type = st.selectbox(
        "Select Report Type",
        ["User Activity Report", "Revenue Report", "Usage Statistics", "Subscription Report"]
    )
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Report Start Date", datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("Report End Date", datetime.now())
    
    if st.button("📊 Generate Report"):
        if report_type == "User Activity Report":
            generate_activity_report(start_date, end_date)
        elif report_type == "Revenue Report":
            generate_revenue_report(start_date, end_date)
        elif report_type == "Usage Statistics":
            generate_usage_report(start_date, end_date)
        elif report_type == "Subscription Report":
            generate_subscription_report()

def show_content_moderation():
    """Content moderation tools"""
    st.header("Content Moderation")
    
    # Recent feedback
    feedback = supabase.table("feedback").select("*").order("created_at", desc=True).limit(20).execute()
    
    if feedback.data:
        st.subheader("Recent Feedback")
        
        for item in feedback.data:
            with st.expander(f"Feedback #{item['id'][:8]} - {item['created_at'][:10]}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**User ID:** {item['user_id']}")
                    st.write(f"**Category:** {item.get('category', 'general')}")
                    st.write(f"**Status:** {item.get('status', 'open')}")
                    st.write(f"**Feedback:** {item['feedback_text']}")
                    if item.get('admin_response'):
                        st.write(f"**Admin Response:** {item['admin_response']}")
                
                with col2:
                    if st.button(f"Flag", key=f"flag_{item['id']}"):
                        update_feedback_status(item['id'], 'flagged')
                        st.success("Flagged")
                        st.experimental_rerun()
                    
                    if st.button(f"Resolve", key=f"resolve_{item['id']}"):
                        update_feedback_status(item['id'], 'resolved')
                        st.success("Resolved")
                        st.experimental_rerun()
                    
                    admin_response = st.text_area(f"Response", key=f"response_{item['id']}")
                    if st.button(f"Reply", key=f"reply_{item['id']}"):
                        if admin_response:
                            add_admin_response(item['id'], admin_response)
                            st.success("Response added")
                            st.experimental_rerun()

# Helper functions
def calculate_monthly_revenue():
    """Calculate monthly revenue"""
    users = supabase.table("users").select("subscription_tier").eq("subscription_status", "active").execute()
    
    pricing = {"basic": 29.99, "premium": 99.99, "enterprise": 299.99}
    total = 0
    
    if users.data:
        for user in users.data:
            tier = user.get("subscription_tier", "basic")
            total += pricing.get(tier, 0)
    
    return total

def get_new_users_today():
    """Get count of new users today"""
    today = datetime.now().date().isoformat()
    users = supabase.table("users").select("*").gte("created_at", today).execute()
    return len(users.data) if users.data else 0

def show_activity_chart():
    """Show activity chart for last 7 days"""
    seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
    activities = supabase.table("user_activity").select("*").gte("created_at", seven_days_ago).execute()
    
    if activities.data:
        df = pd.DataFrame(activities.data)
        df['date'] = pd.to_datetime(df['created_at']).dt.date
        daily_counts = df.groupby('date').size().reset_index(name='count')
        
        fig = px.line(daily_counts, x='date', y='count')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No activity data available")

def show_registration_trend():
    """Show user registration trend"""
    users = supabase.table("users").select("created_at").execute()
    
    if users.data:
        df = pd.DataFrame(users.data)
        df['date'] = pd.to_datetime(df['created_at']).dt.date
        daily_registrations = df.groupby('date').size().reset_index(name='registrations')
        
        fig = px.bar(daily_registrations.tail(30), x='date', y='registrations')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No registration data available")

def show_subscription_pie_chart():
    """Show subscription distribution pie chart"""
    users = supabase.table("users").select("subscription_tier").execute()
    
    if users.data:
        df = pd.DataFrame(users.data)
        tier_counts = df['subscription_tier'].value_counts()
        
        fig = px.pie(values=tier_counts.values, names=tier_counts.index)
        st.plotly_chart(fig, use_container_width=True)

def show_recent_activities():
    """Show recent platform activities"""
    activities = supabase.table("user_activity").select("*").order("created_at", desc=True).limit(10).execute()
    
    if activities.data:
        for activity in activities.data:
            st.write(f"• **{activity['action_type']}** by user {activity['user_id']} at {activity['created_at'][:19]}")
    else:
        st.info("No recent activities")

def show_buying_behavior_analysis(start_date, end_date):
    """Analyze user buying behavior"""
    orders = supabase.table("orders").select("*").gte("created_at", start_date.isoformat()).lte("created_at", end_date.isoformat()).execute()
    
    if orders.data:
        df_orders = pd.DataFrame(orders.data)
        
        # Order status distribution
        status_counts = df_orders['status'].value_counts()
        fig = px.bar(x=status_counts.index, y=status_counts.values, title="Order Status Distribution")
        st.plotly_chart(fig, use_container_width=True)
        
        # Revenue by user
        user_revenue = df_orders.groupby('user_id')['total_amount'].sum().sort_values(ascending=False).head(10)
        st.write("**Top 10 Users by Revenue:**")
        
        for user_id, revenue in user_revenue.items():
            user = supabase.table("users").select("username").eq("id", user_id).execute()
            username = user.data[0]['username'] if user.data else f"User {user_id}"
            st.write(f"• {username}: ${revenue:.2f}")
    else:
        st.info("No order data found for the selected period")

# Database update functions
def update_user_status(user_id, status):
    """Update user subscription status"""
    supabase.table("users").update({"subscription_status": status}).eq("id", user_id).execute()

def update_user_subscription(user_id, tier):
    """Update user subscription tier"""
    supabase.table("users").update({"subscription_tier": tier}).eq("id", user_id).execute()

def toggle_admin_status(user_id, is_admin):
    """Toggle user admin status"""
    supabase.table("users").update({"is_admin": is_admin}).eq("id", user_id).execute()

def update_feedback_status(feedback_id, status):
    """Update feedback status"""
    supabase.table("feedback").update({"status": status, "updated_at": datetime.now().isoformat()}).eq("id", feedback_id).execute()

def add_admin_response(feedback_id, response):
    """Add admin response to feedback"""
    supabase.table("feedback").update({
        "admin_response": response, 
        "status": "in_progress",
        "updated_at": datetime.now().isoformat()
    }).eq("id", feedback_id).execute()

# Report generation functions
def generate_activity_report(start_date, end_date):
    """Generate user activity report"""
    activities = supabase.table("user_activity").select("*").gte("created_at", start_date.isoformat()).lte("created_at", end_date.isoformat()).execute()
    
    if activities.data:
        df = pd.DataFrame(activities.data)
        st.subheader(f"Activity Report ({start_date} to {end_date})")
        st.dataframe(df)
        
        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"activity_report_{start_date}_to_{end_date}.csv",
            mime="text/csv"
        )

def generate_revenue_report(start_date, end_date):
    """Generate revenue report"""
    orders = supabase.table("orders").select("*").gte("created_at", start_date.isoformat()).lte("created_at", end_date.isoformat()).execute()
    
    if orders.data:
        df = pd.DataFrame(orders.data)
        total_revenue = df['total_amount'].sum()
        
        st.subheader(f"Revenue Report ({start_date} to {end_date})")
        st.metric("Total Revenue", f"${total_revenue:.2f}")
        st.dataframe(df)
        
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"revenue_report_{start_date}_to_{end_date}.csv",
            mime="text/csv"
        )

def generate_usage_report(start_date, end_date):
    """Generate usage statistics report"""
    activities = supabase.table("user_activity").select("*").gte("created_at", start_date.isoformat()).lte("created_at", end_date.isoformat()).execute()
    
    if activities.data:
        df = pd.DataFrame(activities.data)
        
        # Usage statistics
        usage_stats = {
            "Total Activities": len(df),
            "Unique Users": df['user_id'].nunique(),
            "Most Common Activity": df['action_type'].mode().iloc[0] if not df.empty else "N/A",
            "Average Activities per User": len(df) / df['user_id'].nunique() if df['user_id'].nunique() > 0 else 0
        }
        
        st.subheader(f"Usage Statistics ({start_date} to {end_date})")
        for key, value in usage_stats.items():
            st.metric(key, value)

def generate_subscription_report():
    """Generate subscription report"""
    users = supabase.table("users").select("*").execute()
    
    if users.data:
        df = pd.DataFrame(users.data)
        
        st.subheader("Subscription Report")
        
        # Subscription breakdown
        tier_counts = df['subscription_tier'].value_counts()
        status_counts = df['subscription_status'].value_counts()
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**By Tier:**")
            for tier, count in tier_counts.items():
                st.write(f"• {tier.title()}: {count}")
        
        with col2:
            st.write("**By Status:**")
            for status, count in status_counts.items():
                st.write(f"• {status.title()}: {count}")
        
        # Revenue calculation
        revenue = calculate_monthly_revenue()
        st.metric("Monthly Recurring Revenue", f"${revenue:.2f}")
        
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="subscription_report.csv",
            mime="text/csv"
        )