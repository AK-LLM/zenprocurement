import streamlit as st
from supabase import create_client, Client
import os
from image_gen import generate_image
from quote import generate_quote_pdf
from datetime import datetime

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# Page setup
st.set_page_config(page_title="AI Procurement MVP", layout="wide")

# Sidebar navigation
page = st.sidebar.selectbox("Navigation", ["Home", "Product Sourcing", "AI Suggestions", "QC Uploads", "Quotes", "Feedback"])

# User authentication placeholder (demo only)
if "user" not in st.session_state:
    st.session_state.user = "demo_user"  # Replace with actual auth logic later

# Home
if page == "Home":
    st.title("AI Procurement MVP")
    st.write("Welcome, ", st.session_state.user)

# Product Sourcing
elif page == "Product Sourcing":
    st.title("Product Sourcing")
    product_query = st.text_input("Enter product search keyword")
    if st.button("Search"):
        st.write(f"Searching for: {product_query}")
        # Log search
        supabase.table("search_logs").insert({
            "user_id": st.session_state.user,
            "search_query": product_query,
            "created_at": datetime.now().isoformat()
        }).execute()
        st.write("Mock search results here. Live supplier API integration in Phase 2.")

# AI Suggestions
elif page == "AI Suggestions":
    st.title("AI Product Suggestions")
    prompt = st.text_area("Enter prompt for product suggestion")
    if st.button("Generate Suggestion"):
        suggestion = f"AI Suggestion for: {prompt}"
        st.write(suggestion)

# QC Uploads
elif page == "QC Uploads":
    st.title("QC Document Upload")
    file = st.file_uploader("Upload QC document")
    if file:
        file_name = file.name
        storage_bucket = supabase.storage().from_("qc_uploads")
        storage_bucket.upload(file_name, file)
        st.success(f"Uploaded {file_name}")

# Quotes
elif page == "Quotes":
    st.title("Generate Quote")
    product_name = st.text_input("Product name")
    quantity = st.number_input("Quantity", min_value=1, step=1)
    if st.button("Generate PDF Quote"):
        pdf_file = generate_quote_pdf(product_name, quantity)
        with open(pdf_file, "rb") as f:
            st.download_button(
                label="Download Quote PDF",
                data=f,
                file_name=pdf_file,
                mime="application/pdf"
            )
        st.success("Quote PDF generated. Click the button above to download.")

# Feedback
elif page == "Feedback":
    st.title("Feedback")
    feedback_text = st.text_area("Enter your feedback")
    if st.button("Submit Feedback"):
        supabase.table("feedback").insert({
            "user_id": st.session_state.user,
            "feedback_text": feedback_text,
            "created_at": datetime.now().isoformat()
        }).execute()
        st.success("Thank you for your feedback.")
