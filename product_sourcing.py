import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import json
from auth import check_subscription_limits, log_user_activity
from supabase import create_client, Client
import os

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

def enhanced_product_sourcing():
    """Enhanced product sourcing with web scraping"""
    st.title("🔍 Enhanced Product Sourcing")
    
    user = st.session_state.user
    
    # Check subscription limits
    if not check_subscription_limits(user["id"], "search"):
        st.error("🚫 You've reached your daily search limit. Please upgrade your subscription.")
        return
    
    # Search interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input("🔍 Enter product search keyword", placeholder="e.g., wireless headphones, office chairs, promotional items")
    
    with col2:
        search_type = st.selectbox("Search Type", ["General", "B2B", "Promotional", "Corporate"])
    
    # Advanced filters
    with st.expander("🔧 Advanced Filters"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            price_range = st.slider("Price Range ($)", 0, 10000, (0, 1000))
            min_quantity = st.number_input("Minimum Quantity", min_value=1, value=1)
        
        with col2:
            category = st.selectbox("Category", [
                "All", "Electronics", "Office Supplies", "Promotional Items", 
                "Apparel", "Industrial", "Healthcare", "Automotive"
            ])
            region = st.selectbox("Supplier Region", ["All", "North America", "Europe", "Asia", "Global"])
        
        with col3:
            quality_rating = st.slider("Minimum Quality Rating", 1, 5, 3)
            certification = st.multiselect("Required Certifications", [
                "ISO 9001", "CE", "FCC", "RoHS", "FDA", "UL"
            ])
    
    # Search button
    if st.button("🚀 Search Products", type="primary"):
        if search_query:
            with st.spinner("Searching products from multiple sources..."):
                # Log the search
                log_user_activity(user["id"], "search", {
                    "query": search_query,
                    "type": search_type,
                    "filters": {
                        "price_range": price_range,
                        "category": category,
                        "region": region,
                        "min_quantity": min_quantity
                    }
                })
                
                # Store search log
                supabase.table("search_logs").insert({
                    "user_id": user["id"],
                    "search_query": search_query,
                    "search_type": search_type.lower(),
                    "filters_applied": {
                        "price_range": price_range,
                        "category": category,
                        "region": region,
                        "quality_rating": quality_rating,
                        "certifications": certification
                    },
                    "created_at": datetime.now().isoformat()
                }).execute()
                
                # Perform web scraping
                results = scrape_product_data(search_query, search_type, {
                    "price_range": price_range,
                    "category": category,
                    "region": region,
                    "min_quantity": min_quantity,
                    "quality_rating": quality_rating,
                    "certifications": certification
                })
                
                # Display results
                display_search_results(results, search_query)
        else:
            st.error("Please enter a search query")
    
    # Recent searches
    st.subheader("📋 Recent Searches")
    show_recent_searches(user["id"])

def scrape_product_data(query, search_type, filters):
    """Scrape product data from multiple sources"""
    results = []
    
    # Simulate web scraping from multiple sources
    # In production, you would scrape from actual B2B platforms
    
    sources = [
        {"name": "Alibaba", "url": f"https://www.alibaba.com/trade/search?SearchText={query}"},
        {"name": "Global Sources", "url": f"https://www.globalsources.com/gsol/I/{query}"},
        {"name": "Made-in-China", "url": f"https://www.made-in-china.com/products-search/hot-china-products/{query}"},
        {"name": "DHgate", "url": f"https://www.dhgate.com/wholesale/search.do?searchkey={query}"},
        {"name": "TradeKey", "url": f"https://www.tradekey.com/ks/{query}"}
    ]
    
    # Mock data generation (replace with actual scraping)
    import random
    
    for i in range(20):  # Generate 20 mock results
        source = random.choice(sources)
        
        # Generate realistic product data
        product = {
            "id": f"prod_{i+1}",
            "name": f"{query.title()} - Model {chr(65+i)}",
            "description": f"High-quality {query} suitable for {search_type.lower()} use. Professional grade with excellent durability.",
            "price": round(random.uniform(filters["price_range"][0], filters["price_range"][1]), 2),
            "min_order_qty": random.randint(filters["min_quantity"], filters["min_quantity"] * 10),
            "supplier": f"Supplier {i+1}",
            "supplier_rating": round(random.uniform(filters["quality_rating"], 5), 1),
            "location": random.choice(["China", "USA", "Germany", "India", "South Korea"]),
            "certifications": random.sample(["ISO 9001", "CE", "FCC", "RoHS"], random.randint(1, 3)),
            "lead_time": f"{random.randint(7, 30)} days",
            "payment_terms": random.choice(["T/T", "L/C", "PayPal", "Western Union"]),
            "source": source["name"],
            "source_url": source["url"],
            "image_url": f"https://via.placeholder.com/200x200?text={query.replace(' ', '+')}"
        }
        
        # Apply filters
        if (filters["price_range"][0] <= product["price"] <= filters["price_range"][1] and
            product["supplier_rating"] >= filters["quality_rating"]):
            
            if filters["category"] == "All" or filters["category"].lower() in product["description"].lower():
                results.append(product)
    
    return results

def display_search_results(results, query):
    """Display search results in an organized manner"""
    if not results:
        st.warning("No products found matching your criteria. Try adjusting your filters.")
        return
    
    st.success(f"Found {len(results)} products for '{query}'")
    
    # Sort options
    col1, col2 = st.columns(2)
    with col1:
        sort_by = st.selectbox("Sort by", ["Price (Low to High)", "Price (High to Low)", "Rating", "Min Order Qty"])
    with col2:
        view_mode = st.radio("View Mode", ["Grid", "List"], horizontal=True)
    
    # Sort results
    if sort_by == "Price (Low to High)":
        results.sort(key=lambda x: x["price"])
    elif sort_by == "Price (High to Low)":
        results.sort(key=lambda x: x["price"], reverse=True)
    elif sort_by == "Rating":
        results.sort(key=lambda x: x["supplier_rating"], reverse=True)
    elif sort_by == "Min Order Qty":
        results.sort(key=lambda x: x["min_order_qty"])
    
    # Display results
    if view_mode == "Grid":
        display_grid_view(results)
    else:
        display_list_view(results)

def display_grid_view(results):
    """Display results in grid view"""
    cols_per_row = 3
    
    for i in range(0, len(results), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j, col in enumerate(cols):
            if i + j < len(results):
                product = results[i + j]
                
                with col:
                    with st.container():
                        st.image(product["image_url"], use_column_width=True)
                        st.subheader(product["name"][:30] + "..." if len(product["name"]) > 30 else product["name"])
                        st.write(f"💰 **${product['price']:.2f}**")
                        st.write(f"📦 Min Order: {product['min_order_qty']}")
                        st.write(f"⭐ Rating: {product['supplier_rating']}/5")
                        st.write(f"📍 {product['location']}")
                        
                        if st.button(f"View Details", key=f"details_{product['id']}"):
                            show_product_details(product)
                        
                        if st.button(f"Add to Quote", key=f"quote_{product['id']}"):
                            add_to_quote(product)

def display_list_view(results):
    """Display results in list view"""
    for product in results:
        with st.expander(f"{product['name']} - ${product['price']:.2f}"):
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                st.image(product["image_url"], width=150)
            
            with col2:
                st.write(f"**Description:** {product['description']}")
                st.write(f"**Supplier:** {product['supplier']} ({product['supplier_rating']}/5 ⭐)")
                st.write(f"**Location:** {product['location']}")
                st.write(f"**Lead Time:** {product['lead_time']}")
                st.write(f"**Payment Terms:** {product['payment_terms']}")
                st.write(f"**Certifications:** {', '.join(product['certifications'])}")
            
            with col3:
                st.metric("Price", f"${product['price']:.2f}")
                st.metric("Min Order", product['min_order_qty'])
                
                if st.button(f"Contact Supplier", key=f"contact_{product['id']}"):
                    contact_supplier(product)
                
                if st.button(f"Add to Quote", key=f"quote_list_{product['id']}"):
                    add_to_quote(product)

def show_product_details(product):
    """Show detailed product information"""
    st.modal("Product Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.image(product["image_url"], width=300)
    
    with col2:
        st.subheader(product["name"])
        st.write(f"**Price:** ${product['price']:.2f}")
        st.write(f"**Minimum Order Quantity:** {product['min_order_qty']}")
        st.write(f"**Supplier:** {product['supplier']}")
        st.write(f"**Rating:** {product['supplier_rating']}/5 ⭐")
        st.write(f"**Location:** {product['location']}")
        st.write(f"**Lead Time:** {product['lead_time']}")
        st.write(f"**Payment Terms:** {product['payment_terms']}")
    
    st.write(f"**Description:** {product['description']}")
    st.write(f"**Certifications:** {', '.join(product['certifications'])}")
    st.write(f"**Source:** {product['source']}")

def add_to_quote(product):
    """Add product to quote"""
    user = st.session_state.user
    
    # Initialize quote session state
    if "quote_items" not in st.session_state:
        st.session_state.quote_items = []
    
    # Add to quote
    quote_item = {
        "product_id": product["id"],
        "name": product["name"],
        "price": product["price"],
        "supplier": product["supplier"],
        "min_order_qty": product["min_order_qty"],
        "added_at": datetime.now().isoformat()
    }
    
    st.session_state.quote_items.append(quote_item)
    
    # Log activity
    log_user_activity(user["id"], "add_to_quote", {
        "product_id": product["id"],
        "product_name": product["name"],
        "price": product["price"]
    })
    
    st.success(f"Added '{product['name']}' to quote!")

def contact_supplier(product):
    """Contact supplier functionality"""
    user = st.session_state.user
    
    st.info(f"Contacting {product['supplier']}...")
    
    # Log activity
    log_user_activity(user["id"], "contact_supplier", {
        "supplier": product["supplier"],
        "product_id": product["id"]
    })
    
    # In production, this would integrate with messaging system
    st.success("Contact request sent to supplier!")

def show_recent_searches(user_id):
    """Show user's recent searches"""
    try:
        searches = supabase.table("search_logs").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(10).execute()
        
        if searches.data:
            for search in searches.data:
                with st.expander(f"🔍 {search['search_query']} - {search['created_at'][:10]}"):
                    st.write(f"**Type:** {search['search_type'].title()}")
                    st.write(f"**Results:** {search.get('results_count', 0)} products found")
                    if search.get('filters_applied'):
                        st.write(f"**Filters:** {json.dumps(search['filters_applied'], indent=2)}")
                    
                    if st.button(f"Search Again", key=f"repeat_{search['id']}"):
                        st.session_state.repeat_search = search['search_query']
                        st.experimental_rerun()
        else:
            st.info("No recent searches found. Start searching to see your history here!")
    
    except Exception as e:
        st.error(f"Error loading search history: {str(e)}")