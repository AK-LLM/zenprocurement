import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from datetime import datetime
from auth import log_user_activity
from supabase import create_client, Client
import os
import requests

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

def branding_manager():
    """Custom branding management system"""
    st.title("🎨 Custom Branding Manager")
    
    user = st.session_state.user
    
    # Load existing branding
    existing_branding = load_user_branding(user["id"])
    
    tab1, tab2, tab3, tab4 = st.tabs(["🏢 Brand Setup", "🎨 Design Tools", "📸 Product Overlay", "📋 Brand Assets"])
    
    with tab1:
        brand_setup_interface(user, existing_branding)
    
    with tab2:
        design_tools_interface(user, existing_branding)
    
    with tab3:
        product_overlay_interface(user, existing_branding)
    
    with tab4:
        brand_assets_interface(user, existing_branding)

def brand_setup_interface(user, existing_branding):
    """Brand setup and configuration"""
    st.header("Brand Configuration")
    
    # Brand information
    col1, col2 = st.columns(2)
    
    with col1:
        brand_name = st.text_input(
            "Brand Name", 
            value=existing_branding.get("brand_name", "") if existing_branding else ""
        )
        
        primary_color = st.color_picker(
            "Primary Brand Color", 
            value=existing_branding.get("primary_color", "#000000") if existing_branding else "#000000"
        )
        
        secondary_color = st.color_picker(
            "Secondary Brand Color", 
            value=existing_branding.get("secondary_color", "#ffffff") if existing_branding else "#ffffff"
        )
    
    with col2:
        font_family = st.selectbox(
            "Brand Font", 
            ["Arial", "Helvetica", "Times New Roman", "Georgia", "Verdana", "Trebuchet MS"],
            index=0 if not existing_branding else ["Arial", "Helvetica", "Times New Roman", "Georgia", "Verdana", "Trebuchet MS"].index(existing_branding.get("font_family", "Arial"))
        )
        
        # Logo upload
        st.subheader("Brand Logo")
        uploaded_logo = st.file_uploader(
            "Upload Logo (PNG/JPG)", 
            type=['png', 'jpg', 'jpeg'],
            help="Recommended: 500x500px, transparent background"
        )
        
        if uploaded_logo:
            st.image(uploaded_logo, width=200, caption="Uploaded Logo")
    
    # Brand guidelines
    st.subheader("Brand Guidelines")
    brand_guidelines = st.text_area(
        "Brand Guidelines & Usage Notes",
        value=existing_branding.get("brand_guidelines", {}).get("notes", "") if existing_branding else "",
        placeholder="Enter brand guidelines, usage instructions, and any specific requirements..."
    )
    
    # Save branding
    if st.button("💾 Save Brand Configuration", type="primary"):
        save_brand_configuration(user["id"], {
            "brand_name": brand_name,
            "primary_color": primary_color,
            "secondary_color": secondary_color,
            "font_family": font_family,
            "brand_guidelines": {"notes": brand_guidelines},
            "logo_uploaded": uploaded_logo is not None
        }, uploaded_logo)

def design_tools_interface(user, existing_branding):
    """Design tools for creating branded materials"""
    st.header("Design Tools")
    
    if not existing_branding:
        st.warning("Please set up your brand configuration first in the Brand Setup tab.")
        return
    
    # Design template selection
    template_type = st.selectbox(
        "Select Design Template",
        ["Business Card", "Letterhead", "Product Label", "Social Media Post", "Banner", "Brochure"]
    )
    
    # Template customization
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(f"{template_type} Designer")
        
        # Text content
        if template_type == "Business Card":
            name = st.text_input("Name", value="John Doe")
            title = st.text_input("Title", value="Manager")
            email = st.text_input("Email", value="john@company.com")
            phone = st.text_input("Phone", value="+1 (555) 123-4567")
            
            content = {"name": name, "title": title, "email": email, "phone": phone}
        
        elif template_type == "Product Label":
            product_name = st.text_input("Product Name", value="Premium Product")
            description = st.text_area("Description", value="High-quality product description")
            price = st.text_input("Price", value="$99.99")
            
            content = {"product_name": product_name, "description": description, "price": price}
        
        else:
            main_text = st.text_input("Main Text", value=f"Your {template_type}")
            subtitle = st.text_input("Subtitle", value="Subtitle text")
            
            content = {"main_text": main_text, "subtitle": subtitle}
        
        # Generate design
        if st.button(f"🎨 Generate {template_type}", type="primary"):
            with st.spinner("Generating design..."):
                design_image = generate_branded_design(template_type, content, existing_branding)
                if design_image:
                    st.image(design_image, caption=f"Generated {template_type}")
                    
                    # Download button
                    img_buffer = io.BytesIO()
                    design_image.save(img_buffer, format='PNG')
                    img_buffer.seek(0)
                    
                    st.download_button(
                        label=f"📥 Download {template_type}",
                        data=img_buffer.getvalue(),
                        file_name=f"{template_type.lower().replace(' ', '_')}.png",
                        mime="image/png"
                    )
                    
                    # Log activity
                    log_user_activity(user["id"], "design_generation", {
                        "template_type": template_type,
                        "brand_name": existing_branding.get("brand_name")
                    })
    
    with col2:
        st.subheader("Brand Preview")
        if existing_branding:
            st.write(f"**Brand:** {existing_branding.get('brand_name', 'N/A')}")
            
            # Color swatches
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"""
                <div style="background-color: {existing_branding.get('primary_color', '#000000')}; 
                           height: 50px; border-radius: 5px; margin: 5px;"></div>
                <p style="text-align: center; font-size: 12px;">Primary</p>
                """, unsafe_allow_html=True)
            
            with col_b:
                st.markdown(f"""
                <div style="background-color: {existing_branding.get('secondary_color', '#ffffff')}; 
                           height: 50px; border-radius: 5px; margin: 5px; border: 1px solid #ccc;"></div>
                <p style="text-align: center; font-size: 12px;">Secondary</p>
                """, unsafe_allow_html=True)
            
            st.write(f"**Font:** {existing_branding.get('font_family', 'Arial')}")

def product_overlay_interface(user, existing_branding):
    """Product image overlay with branding"""
    st.header("Product Branding Overlay")
    
    if not existing_branding:
        st.warning("Please set up your brand configuration first in the Brand Setup tab.")
        return
    
    # Product image upload or URL
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Product Image")
        
        image_source = st.radio("Image Source", ["Upload", "URL", "AI Generated"])
        
        product_image = None
        
        if image_source == "Upload":
            uploaded_image = st.file_uploader("Upload Product Image", type=['png', 'jpg', 'jpeg'])
            if uploaded_image:
                product_image = Image.open(uploaded_image)
                st.image(product_image, width=300, caption="Original Product Image")
        
        elif image_source == "URL":
            image_url = st.text_input("Product Image URL")
            if image_url:
                try:
                    response = requests.get(image_url)
                    product_image = Image.open(io.BytesIO(response.content))
                    st.image(product_image, width=300, caption="Product Image from URL")
                except Exception as e:
                    st.error(f"Error loading image: {str(e)}")
        
        elif image_source == "AI Generated":
            product_prompt = st.text_input("Describe the product for AI generation")
            if st.button("🤖 Generate Product Image") and product_prompt:
                with st.spinner("Generating product image..."):
                    # This would integrate with your existing image generation
                    st.info("AI image generation would be integrated here")
    
    with col2:
        st.subheader("Branding Options")
        
        # Overlay options
        overlay_type = st.selectbox("Overlay Type", [
            "Logo Only", "Logo + Text", "Watermark", "Corner Badge", "Full Branding"
        ])
        
        overlay_position = st.selectbox("Position", [
            "Top Left", "Top Right", "Bottom Left", "Bottom Right", "Center"
        ])
        
        overlay_size = st.slider("Overlay Size (%)", 5, 50, 15)
        overlay_opacity = st.slider("Opacity (%)", 10, 100, 80)
        
        # Additional text
        if overlay_type in ["Logo + Text", "Full Branding"]:
            overlay_text = st.text_input("Overlay Text", value=existing_branding.get("brand_name", ""))
            text_size = st.slider("Text Size", 12, 48, 24)
    
    # Generate branded product image
    if product_image and st.button("🎨 Apply Branding", type="primary"):
        with st.spinner("Applying branding to product image..."):
            branded_image = apply_product_branding(
                product_image, existing_branding, overlay_type, 
                overlay_position, overlay_size, overlay_opacity,
                overlay_text if 'overlay_text' in locals() else None,
                text_size if 'text_size' in locals() else 24
            )
            
            if branded_image:
                st.subheader("Branded Product Image")
                st.image(branded_image, caption="Branded Product Image")
                
                # Download button
                img_buffer = io.BytesIO()
                branded_image.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                
                st.download_button(
                    label="📥 Download Branded Image",
                    data=img_buffer.getvalue(),
                    file_name="branded_product.png",
                    mime="image/png"
                )
                
                # Log activity
                log_user_activity(user["id"], "product_branding", {
                    "overlay_type": overlay_type,
                    "position": overlay_position,
                    "brand_name": existing_branding.get("brand_name")
                })

def brand_assets_interface(user, existing_branding):
    """Brand assets library and management"""
    st.header("Brand Assets Library")
    
    if not existing_branding:
        st.warning("Please set up your brand configuration first in the Brand Setup tab.")
        return
    
    # Asset categories
    asset_category = st.selectbox("Asset Category", [
        "Logos", "Templates", "Color Palettes", "Fonts", "Guidelines", "Generated Designs"
    ])
    
    if asset_category == "Logos":
        show_logo_assets(user, existing_branding)
    elif asset_category == "Templates":
        show_template_assets(user)
    elif asset_category == "Color Palettes":
        show_color_assets(existing_branding)
    elif asset_category == "Guidelines":
        show_brand_guidelines(existing_branding)
    elif asset_category == "Generated Designs":
        show_generated_designs(user)

# Helper functions
def load_user_branding(user_id):
    """Load user's branding configuration"""
    try:
        result = supabase.table("custom_branding").select("*").eq("user_id", user_id).eq("is_active", True).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        st.error(f"Error loading branding: {str(e)}")
        return None

def save_brand_configuration(user_id, branding_data, logo_file):
    """Save brand configuration to database"""
    try:
        # Handle logo upload if provided
        logo_url = None
        if logo_file:
            # In production, upload to Supabase storage
            logo_url = "https://via.placeholder.com/200x200?text=Logo"  # Placeholder
        
        # Deactivate existing branding
        supabase.table("custom_branding").update({"is_active": False}).eq("user_id", user_id).execute()
        
        # Insert new branding
        branding_record = {
            "user_id": user_id,
            "brand_name": branding_data["brand_name"],
            "logo_url": logo_url,
            "primary_color": branding_data["primary_color"],
            "secondary_color": branding_data["secondary_color"],
            "font_family": branding_data["font_family"],
            "brand_guidelines": branding_data["brand_guidelines"],
            "is_active": True,
            "created_at": datetime.now().isoformat()
        }
        
        supabase.table("custom_branding").insert(branding_record).execute()
        
        st.success("Brand configuration saved successfully!")
        
        # Log activity
        log_user_activity(user_id, "brand_setup", {
            "brand_name": branding_data["brand_name"],
            "logo_uploaded": logo_file is not None
        })
        
        st.experimental_rerun()
        
    except Exception as e:
        st.error(f"Error saving branding: {str(e)}")

def generate_branded_design(template_type, content, branding):
    """Generate branded design based on template"""
    try:
        # Create base image
        if template_type == "Business Card":
            img = Image.new('RGB', (600, 350), color=branding.get("secondary_color", "#ffffff"))
        elif template_type == "Product Label":
            img = Image.new('RGB', (400, 300), color=branding.get("secondary_color", "#ffffff"))
        else:
            img = Image.new('RGB', (800, 600), color=branding.get("secondary_color", "#ffffff"))
        
        draw = ImageDraw.Draw(img)
        
        # Add brand colors and text
        primary_color = branding.get("primary_color", "#000000")
        
        # Simple text rendering (in production, use proper font loading)
        if template_type == "Business Card":
            draw.text((50, 50), content["name"], fill=primary_color)
            draw.text((50, 100), content["title"], fill=primary_color)
            draw.text((50, 150), content["email"], fill=primary_color)
            draw.text((50, 200), content["phone"], fill=primary_color)
        
        elif template_type == "Product Label":
            draw.text((50, 50), content["product_name"], fill=primary_color)
            draw.text((50, 100), content["description"], fill=primary_color)
            draw.text((50, 200), content["price"], fill=primary_color)
        
        else:
            draw.text((100, 200), content["main_text"], fill=primary_color)
            draw.text((100, 300), content["subtitle"], fill=primary_color)
        
        # Add brand name
        brand_name = branding.get("brand_name", "")
        if brand_name:
            draw.text((img.width - 200, img.height - 50), brand_name, fill=primary_color)
        
        return img
        
    except Exception as e:
        st.error(f"Error generating design: {str(e)}")
        return None

def apply_product_branding(product_image, branding, overlay_type, position, size, opacity, text=None, text_size=24):
    """Apply branding overlay to product image"""
    try:
        # Create a copy of the product image
        branded_img = product_image.copy()
        
        # Create overlay
        overlay = Image.new('RGBA', branded_img.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Calculate position
        img_width, img_height = branded_img.size
        overlay_width = int(img_width * size / 100)
        overlay_height = int(img_height * size / 100)
        
        positions = {
            "Top Left": (20, 20),
            "Top Right": (img_width - overlay_width - 20, 20),
            "Bottom Left": (20, img_height - overlay_height - 20),
            "Bottom Right": (img_width - overlay_width - 20, img_height - overlay_height - 20),
            "Center": ((img_width - overlay_width) // 2, (img_height - overlay_height) // 2)
        }
        
        x, y = positions[position]
        
        # Add branding elements
        primary_color = branding.get("primary_color", "#000000")
        
        if overlay_type in ["Logo Only", "Logo + Text", "Full Branding"]:
            # Placeholder for logo (in production, load actual logo)
            overlay_draw.rectangle([x, y, x + overlay_width, y + overlay_height], 
                                 fill=primary_color + f"{int(opacity * 2.55):02x}")
        
        if overlay_type in ["Logo + Text", "Full Branding"] and text:
            # Add text
            overlay_draw.text((x + 10, y + overlay_height + 10), text, 
                            fill=primary_color + f"{int(opacity * 2.55):02x}")
        
        # Composite the overlay onto the product image
        branded_img = Image.alpha_composite(branded_img.convert('RGBA'), overlay)
        
        return branded_img.convert('RGB')
        
    except Exception as e:
        st.error(f"Error applying branding: {str(e)}")
        return None

def show_logo_assets(user, branding):
    """Show logo assets"""
    st.subheader("Logo Assets")
    
    if branding.get("logo_url"):
        st.image(branding["logo_url"], width=200, caption="Current Logo")
    else:
        st.info("No logo uploaded yet. Upload a logo in the Brand Setup tab.")
    
    # Logo variations
    st.write("**Logo Variations:**")
    st.write("• Primary Logo")
    st.write("• Secondary Logo")
    st.write("• Monochrome Version")
    st.write("• Icon Only")

def show_template_assets(user):
    """Show template assets"""
    st.subheader("Design Templates")
    
    templates = [
        "Business Card Template",
        "Letterhead Template", 
        "Product Label Template",
        "Social Media Template",
        "Banner Template"
    ]
    
    for template in templates:
        with st.expander(template):
            st.write(f"Template: {template}")
            st.button(f"Use {template}", key=f"use_{template}")

def show_color_assets(branding):
    """Show color palette"""
    st.subheader("Brand Colors")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style="background-color: {branding.get('primary_color', '#000000')}; 
                   height: 100px; border-radius: 10px; margin: 10px;"></div>
        <p><strong>Primary Color:</strong> {branding.get('primary_color', '#000000')}</p>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background-color: {branding.get('secondary_color', '#ffffff')}; 
                   height: 100px; border-radius: 10px; margin: 10px; border: 1px solid #ccc;"></div>
        <p><strong>Secondary Color:</strong> {branding.get('secondary_color', '#ffffff')}</p>
        """, unsafe_allow_html=True)

def show_brand_guidelines(branding):
    """Show brand guidelines"""
    st.subheader("Brand Guidelines")
    
    guidelines = branding.get("brand_guidelines", {}).get("notes", "No guidelines set.")
    st.write(guidelines)
    
    st.write("**Usage Guidelines:**")
    st.write("• Logo minimum size: 50px")
    st.write("• Clear space: 2x logo height")
    st.write("• Approved color combinations only")
    st.write("• Maintain aspect ratio")

def show_generated_designs(user):
    """Show previously generated designs"""
    st.subheader("Generated Designs")
    
    # In production, load from database
    st.info("Your generated designs will appear here after creating them in the Design Tools tab.")