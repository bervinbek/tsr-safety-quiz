import streamlit as st
import requests
import json
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import time
import base64
import urllib.parse
import os

# Try importing the new Google GenAI library
try:
    from google import genai
    NEW_GENAI = True
except ImportError:
    NEW_GENAI = False
    # Fallback to old library
    try:
        import google.generativeai as genai
        NEW_GENAI = False
    except ImportError:
        genai = None

def generate_realistic_fallback():
    """
    Generate a realistic image using free AI services when Gemini is unavailable.
    Always returns a photorealistic image, never an illustration.
    """
    try:
        # Use Pollinations AI with highly detailed prompt for realistic output
        realistic_prompt = """
        Ultra-realistic photograph, professional DSLR quality, sharp focus, natural lighting:
        Two Asian male soldiers aged 20, military training accident scene. One soldier sitting on asphalt 
        road holding injured ankle with pained expression, wearing green camouflage military uniform, 
        tactical vest, backpack, combat boots. Second soldier standing and bending down to help, 
        same uniform. Military training ground, tropical trees, concrete buildings background.
        Harsh sunlight, documentary photography style, high detail, photorealistic, NOT cartoon.
        """
        
        encoded_prompt = urllib.parse.quote(realistic_prompt)
        
        # Use Flux model for best realistic quality
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=400&model=flux&seed={int(time.time())}&nologo=true"
        
        with st.spinner("Generating realistic fallback image..."):
            response = requests.get(image_url, timeout=45)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                img_with_text = add_model_attribution(img, "AI Generated (Fallback)")
                return img_with_text
    except Exception as e:
        st.error(f"Failed to generate realistic image: {e}")
    
    # If absolutely everything fails, return None rather than illustration
    st.error("Unable to generate image. Please check your internet connection.")
    return None

def create_scenario_illustration():
    """
    Create a simple illustrated diagram for the safety scenario.
    This creates a basic visual representation without requiring external APIs.
    """
    try:
        # Create a new image with a light background
        width, height = 800, 400
        img = Image.new('RGB', (width, height), color='#f0f8ff')
        draw = ImageDraw.Draw(img)
        
        # Draw ground line
        draw.line([(0, 320), (800, 320)], fill='#8B7355', width=3)
        
        # Draw trees/forest background (simple representation)
        for x in range(50, 750, 100):
            # Tree trunk
            draw.rectangle([(x, 250), (x+20, 320)], fill='#8B4513')
            # Tree top (triangle)
            draw.polygon([(x-20, 250), (x+10, 180), (x+40, 250)], fill='#228B22')
        
        # Draw fallen SAF soldier (simplified)
        # Body on ground - pixelated uniform colors
        draw.ellipse([(250, 290), (280, 310)], fill='#6b7a4a')  # torso (SAF green)
        draw.ellipse([(240, 295), (255, 310)], fill='#d4a574')  # head (Asian skin tone)
        # Draw jockey cap
        draw.ellipse([(238, 293), (257, 303)], fill='#4a5d23')  # SAF cap
        # Arms
        draw.line([(265, 300), (235, 285)], fill='#6b7a4a', width=3)
        draw.line([(265, 300), (295, 285)], fill='#6b7a4a', width=3)
        # Legs (one bent showing injury) - holding ankle
        draw.line([(265, 305), (245, 330)], fill='#6b7a4a', width=3)
        draw.line([(265, 305), (285, 325)], fill='#6b7a4a', width=3)
        draw.ellipse([(283, 323), (288, 328)], fill='#ff0000')  # injury indicator
        # Field pack
        draw.rectangle([(280, 285), (300, 305)], fill='#4a5d23')  # SAF green pack
        # LBV vest
        draw.rectangle([(255, 295), (275, 308)], fill='#3d4a2e', outline='#2a3420')
        
        # Draw standing SAF soldier (simplified)
        # Body standing - pixelated uniform
        draw.ellipse([(420, 240), (450, 280)], fill='#6b7a4a')  # torso
        draw.ellipse([(425, 225), (445, 245)], fill='#d4a574')  # head
        # Jockey cap
        draw.ellipse([(423, 223), (447, 233)], fill='#4a5d23')
        # Arms (reaching down to help)
        draw.line([(435, 260), (405, 290)], fill='#6b7a4a', width=3)  # reaching down
        draw.line([(435, 260), (455, 270)], fill='#6b7a4a', width=3)
        # Legs
        draw.line([(435, 280), (425, 320)], fill='#6b7a4a', width=3)
        draw.line([(435, 280), (445, 320)], fill='#6b7a4a', width=3)
        # Field pack
        draw.rectangle([(450, 250), (470, 275)], fill='#4a5d23')
        # LBV vest
        draw.rectangle([(425, 245), (445, 278)], fill='#3d4a2e', outline='#2a3420')
        
        # Add warning/attention symbol
        draw.polygon([(350, 200), (340, 220), (360, 220)], fill='#ff0000', outline='#ff0000')
        draw.ellipse([(347, 225), (353, 231)], fill='#ff0000')
        
        # Add text labels
        try:
            # Try to use default font, fallback to basic if not available
            font = ImageFont.truetype("arial.ttf", 20)
            small_font = ImageFont.truetype("arial.ttf", 14)
        except:
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        draw.text((250, 30), "SAF Safety Scenario: Route March Injury", fill='#000080', font=font)
        draw.text((200, 340), "Injured NSF", fill='#333333', font=small_font)
        draw.text((400, 340), "Buddy", fill='#333333', font=small_font)
        draw.text((50, 370), "Action Required: Assess, Alert Safety IC/Medic, Do Not Move if Serious", fill='#8B0000', font=small_font)
        
        return img
        
    except Exception as e:
        st.error(f"Error creating illustration: {e}")
        return None

def add_model_attribution(img, model_name):
    """
    Add small text attribution to the image showing which model generated it.
    """
    try:
        # Create a copy to avoid modifying the original
        img_with_text = img.copy()
        draw = ImageDraw.Draw(img_with_text)
        
        # Try to use a small font
        try:
            font = ImageFont.truetype("arial.ttf", 10)
        except:
            font = ImageFont.load_default()
        
        # Add semi-transparent background for better text visibility
        text = f"Generated by: {model_name}"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Position in bottom right corner
        x = img.width - text_width - 10
        y = img.height - text_height - 10
        
        # Draw background for better text visibility
        draw.rectangle([(x-5, y-2), (x + text_width + 5, y + text_height + 2)], 
                      fill='black')
        
        # Draw the text
        draw.text((x, y), text, fill='white', font=font)
        
        return img_with_text
    except Exception as e:
        print(f"Error adding attribution: {e}")
        return img

def generate_safety_scenario_image():
    """
    Generate image using Google Gemini 2.0 Flash Image Preview.
    Uses the new native image generation capabilities.
    """
    
    # Enhanced prompt for photorealistic output with Gemini
    image_prompt = """
    Generate a highly realistic, photographic quality image. Style: Professional military documentary photography, 
    Canon 5D Mark IV, 85mm lens, natural lighting, high detail, sharp focus.
    
    Subject: Two Asian male soldiers (age 19-21) in Singapore Armed Forces uniforms during training exercise.
    
    Details:
    - Uniforms: Authentic SAF pixelated digital camouflage pattern (green/brown/black), tactical vests, 
      field backpacks, military caps, black combat boots
    - Action: One soldier sitting on ground holding injured ankle with pained expression, second soldier 
      standing and bending down to help
    - Environment: Military training ground, asphalt road, tropical trees, military buildings in background
    - Lighting: Bright daylight, harsh sun creating realistic shadows
    - Quality: Photorealistic, high resolution, documentary style, not illustrated or cartoon
    
    Emphasis on realism: Make this look like an actual photograph taken during military training, 
    with authentic details, natural poses, realistic lighting and shadows.
    """
    
    try:
        # Get Google API key
        google_api_key = None
        try:
            google_api_key = st.secrets.get("GOOGLE_API_KEY", "")
            if not google_api_key or google_api_key == "":
                st.error("Google API Key is required. Please add GOOGLE_API_KEY to .streamlit/secrets.toml")
                # Use a high-quality realistic fallback image service
                return generate_realistic_fallback()
        except:
            st.error("Google API Key not found. Please add GOOGLE_API_KEY to .streamlit/secrets.toml")
            return generate_realistic_fallback()
        
        if not genai:
            st.error("Google GenAI library not installed. Run: pip install google-genai")
            return generate_realistic_fallback()
            
        with st.spinner("Generating SAF scenario image with Gemini 2.0 Flash Image..."):
            try:
                if NEW_GENAI:
                    # Use the new google-genai library with image generation
                    client = genai.Client(api_key=google_api_key)
                    
                    # Add system instruction for photorealistic output
                    system_instruction = """You are a photorealistic image generator. 
                    Generate only highly realistic, photograph-quality images that look like actual photos.
                    Avoid any cartoon, illustration, or artistic styles. Focus on documentary realism."""
                    
                    # Generate image using Gemini 2.0 Flash Image Preview with enhanced prompt
                    full_prompt = f"{system_instruction}\n\n{image_prompt}"
                    
                    response = client.models.generate_content(
                        model="gemini-2.0-flash-image-preview",
                        contents=[full_prompt]
                    )
                    
                    # Extract the generated image from response
                    for part in response.candidates[0].content.parts:
                        if part.inline_data is not None:
                            # Image data is in the inline_data
                            img = Image.open(BytesIO(part.inline_data.data))
                            # Resize if needed
                            if img.size != (800, 400):
                                img = img.resize((800, 400), Image.Resampling.LANCZOS)
                            # Add attribution
                            img_with_text = add_model_attribution(img, "Gemini 2.0 Flash Image")
                            return img_with_text
                        elif part.text is not None:
                            # Sometimes the model returns text explaining the image
                            st.info(f"Gemini response: {part.text[:200]}")
                    
                    # If no image was generated, try alternative approach
                    st.warning("Gemini didn't generate an image directly. Using enhanced prompt approach.")
                    
                # Fallback if new API doesn't work
                st.warning("Gemini 2.0 Flash Image Preview not available. Using realistic fallback.")
                return generate_realistic_fallback()
                    
            except Exception as e:
                st.error(f"Gemini generation error: {e}")
                # Use realistic fallback if Gemini fails
                return generate_realistic_fallback()
            
    except Exception as e:
        # If Gemini API key issues or other errors
        print(f"Image generation error: {e}")
        st.error(f"Gemini 2.0 Flash Image generation failed. Using realistic fallback.")
        return generate_realistic_fallback()

def get_cached_scenario_image():
    """
    Get or generate the scenario image with caching to avoid repeated API calls.
    """
    if 'scenario_image' not in st.session_state:
        with st.spinner("Generating scenario visualization..."):
            image = generate_safety_scenario_image()
            if image:
                st.session_state.scenario_image = image
    
    return st.session_state.get('scenario_image', None)