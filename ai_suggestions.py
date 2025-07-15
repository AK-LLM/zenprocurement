import streamlit as st
import openai
import os
from datetime import datetime
from auth import check_subscription_limits, log_user_activity
from supabase import create_client, Client
from image_gen import generate_image
import json

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

def industry_ai_suggestions():
    """AI-powered product suggestions for different industries"""
    st.title("🤖 AI Product Suggestions")
    
    user = st.session_state.user
    
    # Check subscription limits
    if not check_subscription_limits(user["id"], "ai_suggestion"):
        st.error("🚫 You've reached your daily AI suggestion limit. Please upgrade your subscription.")
        return
    
    # Industry selection
    col1, col2 = st.columns(2)
    
    with col1:
        industry = st.selectbox("🏢 Select Industry", [
            "Banking & Finance",
            "Formula 1 & Motorsports", 
            "Shipping & Logistics",
            "Healthcare",
            "Technology",
            "Manufacturing",
            "Retail",
            "Education",
            "Hospitality",
            "Real Estate",
            "Legal Services",
            "Consulting"
        ])
    
    with col2:
        use_case = st.selectbox("📋 Use Case", [
            "Corporate Gifts",
            "Employee Merchandise",
            "Client Appreciation",
            "Trade Show Items",
            "Office Supplies",
            "Safety Equipment",
            "Branding Materials",
            "Event Supplies",
            "Operational Tools",
            "Custom Solutions"
        ])
    
    # Advanced parameters
    with st.expander("🔧 Advanced Parameters"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            budget_range = st.slider("Budget per Item ($)", 1, 1000, (10, 100))
            quantity = st.number_input("Expected Quantity", min_value=1, value=100)
        
        with col2:
            target_audience = st.selectbox("Target Audience", [
                "Executives", "Employees", "Clients", "Partners", 
                "General Public", "Specialists", "Students"
            ])
            urgency = st.selectbox("Urgency", ["Low", "Medium", "High", "Urgent"])
        
        with col3:
            sustainability = st.checkbox("Eco-friendly preferred")
            customization = st.checkbox("Customization required")
            premium_quality = st.checkbox("Premium quality only")
    
    # Custom prompt
    custom_prompt = st.text_area(
        "💬 Additional Requirements (Optional)", 
        placeholder="e.g., Must be portable, suitable for outdoor use, tech-savvy audience..."
    )
    
    # Generate suggestions
    if st.button("🚀 Generate AI Suggestions", type="primary"):
        with st.spinner("AI is analyzing your requirements and generating suggestions..."):
            
            # Log activity
            log_user_activity(user["id"], "ai_suggestion", {
                "industry": industry,
                "use_case": use_case,
                "budget_range": budget_range,
                "quantity": quantity,
                "custom_prompt": custom_prompt
            })
            
            # Generate suggestions
            suggestions = generate_industry_suggestions(
                industry, use_case, budget_range, quantity, 
                target_audience, urgency, sustainability, 
                customization, premium_quality, custom_prompt
            )
            
            # Display suggestions
            display_suggestions(suggestions, industry, use_case)
            
            # Store suggestions in database
            store_suggestions(user["id"], industry, suggestions)

def generate_industry_suggestions(industry, use_case, budget_range, quantity, 
                                target_audience, urgency, sustainability, 
                                customization, premium_quality, custom_prompt):
    """Generate AI-powered product suggestions"""
    
    # Industry-specific prompts
    industry_contexts = {
        "Banking & Finance": {
            "context": "Professional, trustworthy, sophisticated financial services environment",
            "keywords": ["professional", "elegant", "trustworthy", "premium", "corporate"],
            "avoid": ["flashy", "casual", "cheap-looking"]
        },
        "Formula 1 & Motorsports": {
            "context": "High-speed, precision, technology-driven motorsports industry",
            "keywords": ["speed", "precision", "technology", "performance", "racing"],
            "avoid": ["slow", "outdated", "low-tech"]
        },
        "Shipping & Logistics": {
            "context": "Global trade, efficiency, reliability, supply chain management",
            "keywords": ["efficient", "durable", "global", "reliable", "logistics"],
            "avoid": ["fragile", "local-only", "unreliable"]
        },
        "Healthcare": {
            "context": "Medical, sterile, safety-focused, patient care environment",
            "keywords": ["medical-grade", "sterile", "safe", "healthcare", "professional"],
            "avoid": ["non-medical", "unsafe", "unprofessional"]
        }
    }
    
    context = industry_contexts.get(industry, {
        "context": f"{industry} professional environment",
        "keywords": ["professional", "quality", "branded"],
        "avoid": ["unprofessional", "low-quality"]
    })
    
    # Build comprehensive prompt
    prompt = f"""
    Generate 5 specific product suggestions for {industry} industry, {use_case} use case.
    
    Context: {context['context']}
    Target Audience: {target_audience}
    Budget Range: ${budget_range[0]} - ${budget_range[1]} per item
    Quantity: {quantity} items
    Urgency: {urgency}
    
    Requirements:
    - Sustainability focus: {sustainability}
    - Customization needed: {customization}
    - Premium quality only: {premium_quality}
    
    Additional requirements: {custom_prompt}
    
    For each product, provide:
    1. Product name
    2. Detailed description (2-3 sentences)
    3. Why it's perfect for {industry}
    4. Estimated price range
    5. Customization options
    6. Supplier recommendations
    7. Lead time estimate
    8. Sustainability features (if applicable)
    
    Focus on products that incorporate these keywords: {', '.join(context['keywords'])}
    Avoid products that are: {', '.join(context['avoid'])}
    """
    
    # Mock AI response (replace with actual OpenAI API call)
    suggestions = generate_mock_suggestions(industry, use_case, budget_range, quantity)
    
    return suggestions

def generate_mock_suggestions(industry, use_case, budget_range, quantity):
    """Generate mock suggestions (replace with actual AI API)"""
    
    # Industry-specific product templates
    product_templates = {
        "Banking & Finance": [
            {
                "name": "Premium Leather Portfolio with Logo Embossing",
                "description": "Sophisticated leather portfolio perfect for client meetings and presentations. Features multiple card slots, document compartments, and premium gold embossing.",
                "why_perfect": "Conveys professionalism and attention to detail that banking clients expect",
                "price_range": [45, 85],
                "customization": ["Logo embossing", "Color selection", "Interior layout"],
                "suppliers": ["Premium Leather Co.", "Executive Gifts Ltd."],
                "lead_time": "14-21 days",
                "sustainability": "Ethically sourced leather, recyclable packaging"
            },
            {
                "name": "Smart Wireless Charging Desk Pad",
                "description": "Premium desk pad with built-in wireless charging zones and cable management. Made from sustainable materials with anti-slip base.",
                "why_perfect": "Modern tech solution that enhances productivity in financial workspaces",
                "price_range": [35, 65],
                "customization": ["Logo printing", "Color options", "Size variations"],
                "suppliers": ["TechDesk Solutions", "Modern Office Supply"],
                "lead_time": "10-15 days",
                "sustainability": "Made from recycled materials, energy-efficient charging"
            }
        ],
        "Formula 1 & Motorsports": [
            {
                "name": "Carbon Fiber Business Card Holder",
                "description": "Sleek business card holder made from authentic carbon fiber material. Lightweight yet durable with racing-inspired design elements.",
                "why_perfect": "Reflects the high-tech, performance-oriented nature of motorsports",
                "price_range": [25, 45],
                "customization": ["Team colors", "Logo engraving", "Racing stripes"],
                "suppliers": ["Carbon Craft Co.", "Racing Accessories Ltd."],
                "lead_time": "7-14 days",
                "sustainability": "Recyclable carbon fiber, minimal packaging"
            },
            {
                "name": "Precision Titanium Multi-Tool",
                "description": "Professional-grade multi-tool crafted from aerospace titanium. Features precision instruments perfect for technical professionals.",
                "why_perfect": "Embodies the precision and high-performance standards of F1",
                "price_range": [55, 95],
                "customization": ["Laser engraving", "Tool selection", "Carrying case"],
                "suppliers": ["Precision Tools Inc.", "Titanium Craft"],
                "lead_time": "21-28 days",
                "sustainability": "Durable titanium reduces replacement needs"
            }
        ]
    }
    
    # Get templates for industry or use generic ones
    templates = product_templates.get(industry, [
        {
            "name": f"Custom {use_case} Solution",
            "description": f"Professional solution designed specifically for {industry} {use_case} needs.",
            "why_perfect": f"Tailored to meet the specific requirements of {industry} professionals",
            "price_range": budget_range,
            "customization": ["Logo printing", "Color options", "Custom packaging"],
            "suppliers": ["Professional Supply Co.", "Industry Solutions Ltd."],
            "lead_time": "14-21 days",
            "sustainability": "Eco-friendly materials and packaging"
        }
    ])
    
    # Generate 5 suggestions
    suggestions = []
    for i in range(5):
        if i < len(templates):
            suggestion = templates[i].copy()
        else:
            # Generate variations
            base = templates[i % len(templates)].copy()
            base["name"] = f"{base['name']} - Variant {i+1}"
            suggestion = base
        
        # Add image generation prompt
        suggestion["image_prompt"] = f"{suggestion['name']} for {industry} professional use, high quality product photography"
        suggestions.append(suggestion)
    
    return suggestions

def display_suggestions(suggestions, industry, use_case):
    """Display AI-generated suggestions"""
    st.success(f"Generated {len(suggestions)} AI suggestions for {industry} - {use_case}")
    
    for i, suggestion in enumerate(suggestions, 1):
        with st.expander(f"💡 Suggestion {i}: {suggestion['name']}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Description:** {suggestion['description']}")
                st.write(f"**Why Perfect for {industry}:** {suggestion['why_perfect']}")
                st.write(f"**Price Range:** ${suggestion['price_range'][0]} - ${suggestion['price_range'][1]}")
                st.write(f"**Lead Time:** {suggestion['lead_time']}")
                st.write(f"**Customization Options:** {', '.join(suggestion['customization'])}")
                st.write(f"**Recommended Suppliers:** {', '.join(suggestion['suppliers'])}")
                if suggestion.get('sustainability'):
                    st.write(f"**Sustainability:** {suggestion['sustainability']}")
            
            with col2:
                # Generate product image
                if st.button(f"🎨 Generate Image", key=f"img_{i}"):
                    with st.spinner("Generating product image..."):
                        user = st.session_state.user
                        
                        # Check image generation limits
                        if check_subscription_limits(user["id"], "image_generation"):
                            image_url = generate_image(suggestion["image_prompt"])
                            if image_url:
                                st.image(image_url, caption=suggestion['name'])
                                
                                # Log activity
                                log_user_activity(user["id"], "image_generation", {
                                    "product_name": suggestion['name'],
                                    "prompt": suggestion["image_prompt"]
                                })
                            else:
                                st.error("Failed to generate image")
                        else:
                            st.error("Daily image generation limit reached")
                
                # Action buttons
                if st.button(f"📋 Add to Quote", key=f"quote_{i}"):
                    add_suggestion_to_quote(suggestion)
                
                if st.button(f"🔍 Find Suppliers", key=f"suppliers_{i}"):
                    find_suppliers_for_suggestion(suggestion)
                
                if st.button(f"⭐ Save Favorite", key=f"fav_{i}"):
                    save_favorite_suggestion(suggestion)

def add_suggestion_to_quote(suggestion):
    """Add AI suggestion to quote"""
    user = st.session_state.user
    
    if "quote_items" not in st.session_state:
        st.session_state.quote_items = []
    
    quote_item = {
        "type": "ai_suggestion",
        "name": suggestion["name"],
        "description": suggestion["description"],
        "price_range": suggestion["price_range"],
        "customization": suggestion["customization"],
        "suppliers": suggestion["suppliers"],
        "lead_time": suggestion["lead_time"],
        "added_at": datetime.now().isoformat()
    }
    
    st.session_state.quote_items.append(quote_item)
    
    log_user_activity(user["id"], "add_suggestion_to_quote", {
        "suggestion_name": suggestion["name"]
    })
    
    st.success(f"Added '{suggestion['name']}' to quote!")

def find_suppliers_for_suggestion(suggestion):
    """Find suppliers for AI suggestion"""
    user = st.session_state.user
    
    st.info(f"Searching suppliers for {suggestion['name']}...")
    
    # Mock supplier search results
    suppliers = [
        {
            "name": supplier,
            "rating": 4.2 + (hash(supplier) % 8) / 10,
            "location": ["China", "USA", "Germany", "India"][hash(supplier) % 4],
            "min_order": 50 + (hash(supplier) % 200),
            "lead_time": f"{7 + (hash(supplier) % 21)} days"
        }
        for supplier in suggestion["suppliers"]
    ]
    
    for supplier in suppliers:
        st.write(f"**{supplier['name']}** - ⭐ {supplier['rating']}/5")
        st.write(f"📍 {supplier['location']} | 📦 Min Order: {supplier['min_order']} | ⏱️ {supplier['lead_time']}")
    
    log_user_activity(user["id"], "supplier_search", {
        "suggestion_name": suggestion["name"],
        "suppliers_found": len(suppliers)
    })

def save_favorite_suggestion(suggestion):
    """Save suggestion as favorite"""
    user = st.session_state.user
    
    # Store in database
    try:
        supabase.table("product_suggestions").insert({
            "user_id": user["id"],
            "industry_segment": "favorite",
            "prompt": f"Favorite: {suggestion['name']}",
            "suggestion_data": suggestion,
            "created_at": datetime.now().isoformat()
        }).execute()
        
        log_user_activity(user["id"], "save_favorite", {
            "suggestion_name": suggestion["name"]
        })
        
        st.success("Saved to favorites!")
    except Exception as e:
        st.error(f"Error saving favorite: {str(e)}")

def store_suggestions(user_id, industry, suggestions):
    """Store suggestions in database for analytics"""
    try:
        for suggestion in suggestions:
            supabase.table("product_suggestions").insert({
                "user_id": user_id,
                "industry_segment": industry,
                "prompt": f"{industry} suggestions",
                "suggestion_data": suggestion,
                "created_at": datetime.now().isoformat()
            }).execute()
    except Exception as e:
        st.error(f"Error storing suggestions: {str(e)}")

# Show recent suggestions
def show_recent_suggestions():
    """Show user's recent AI suggestions"""
    user = st.session_state.user
    
    st.subheader("📋 Recent AI Suggestions")
    
    try:
        suggestions = supabase.table("product_suggestions").select("*").eq("user_id", user["id"]).order("created_at", desc=True).limit(10).execute()
        
        if suggestions.data:
            for suggestion in suggestions.data:
                with st.expander(f"💡 {suggestion['suggestion_data']['name']} - {suggestion['created_at'][:10]}"):
                    st.json(suggestion['suggestion_data'])
        else:
            st.info("No recent suggestions found.")
    except Exception as e:
        st.error(f"Error loading suggestions: {str(e)}")