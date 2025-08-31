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
    # Get selected model from session state
    selected_model = st.session_state.get('selected_image_model', 'Auto (Best)')
    
    # Import quiz_config here to avoid circular imports
    from quiz_config import load_quiz_config
    
    try:
        # Check if there's a specific prompt in session state (for multi-question support)
        if 'current_gen_prompt' in st.session_state:
            base_prompt = st.session_state.get('current_gen_prompt', "")
        else:
            # Load prompt from configuration
            config = load_quiz_config()
            base_prompt = config.get("image_prompt", "")
        
        # Different prompts for different models
        if selected_model == "Simplified":
            # Use a simplified version of the prompt
            if base_prompt and base_prompt.strip():
                # Extract key elements from the configured prompt
                realistic_prompt = "Two soldiers military training one injured helping Singapore modern uniforms"
            else:
                realistic_prompt = "Two soldiers military training one injured helping Singapore modern uniforms"
        else:
            # Use the full configured prompt or default
            if base_prompt and base_prompt.strip():
                realistic_prompt = base_prompt
            else:
                # Detailed prompt for better models
                realistic_prompt = """
                Photorealistic photo: Two Asian soldiers in modern Singapore military pixelated camouflage uniforms.
                One soldier sitting on ground holding injured ankle. Second soldier helping.
                Military training camp, tropical setting, documentary style, realistic lighting.
                """
        
        encoded_prompt = urllib.parse.quote(realistic_prompt)
        
        # Determine which models to try based on selection
        # Note: Pollinations.ai may have limited model support, so we'll use their default with style hints
        if selected_model == "Flux (Realistic)":
            # Add style hints for realistic output
            styled_prompt = f"{realistic_prompt}, ultra realistic, photorealistic, high quality photography"
            models = [("default", styled_prompt)]
        elif selected_model == "Turbo (Fast)":
            # Use simpler prompt for faster generation
            models = [("default", realistic_prompt)]
        elif selected_model == "Simplified":
            # Use very simple prompt
            simple = "Two soldiers military training one injured helping Singapore modern uniforms"
            models = [("default", simple)]
        else:  # Auto (Best)
            # Try different style variations
            styled_prompt = f"{realistic_prompt}, ultra realistic, photorealistic, high quality photography"
            models = [("default", styled_prompt), ("default", realistic_prompt)]
        
        for model_name, prompt_to_use in models:
            try:
                # Encode the specific prompt for this attempt
                encoded_prompt_specific = urllib.parse.quote(prompt_to_use)
                # Pollinations.ai doesn't use model parameter in the same way - remove it
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt_specific}?width=800&height=400&seed={int(time.time())}"
                
                # No nested spinner - just make the request
                response = requests.get(image_url, timeout=60, headers={'User-Agent': 'Mozilla/5.0'})
                    
                if response.status_code == 200:
                    # Verify we got an image
                    content_type = response.headers.get('content-type', '')
                    if 'image' in content_type:
                        img = Image.open(BytesIO(response.content))
                        # Show which model/style was selected
                        attribution = f"AI Generated ({selected_model})"
                        img_with_text = add_model_attribution(img, attribution)
                        # Clean up the prompt from session state after successful generation
                        if 'current_gen_prompt' in st.session_state:
                            del st.session_state.current_gen_prompt
                        return img_with_text
                    else:
                        # Don't show warning for each attempt in Auto mode
                        if selected_model != "Auto (Best)":
                            st.warning(f"Received non-image response")
                        continue
                else:
                    # Don't show warning for each attempt in Auto mode
                    if selected_model != "Auto (Best)":
                        st.warning(f"Generation returned status {response.status_code}")
                    continue
                        
            except requests.exceptions.Timeout:
                # Only show timeout warning if not in Auto mode
                if selected_model != "Auto (Best)":
                    st.warning(f"Request timeout - please try again")
                continue
            except Exception as e:
                # Only show error if not in Auto mode
                if selected_model != "Auto (Best)":
                    st.warning(f"Generation error: {str(e)[:100]}")
                continue
        
        # Last resort - use a very simple prompt
        simple_prompt = "Two soldiers military training one injured helping Singapore"
        encoded_simple = urllib.parse.quote(simple_prompt)
        simple_url = f"https://image.pollinations.ai/prompt/{encoded_simple}?width=800&height=400&seed={int(time.time())}"
        
        try:
            response = requests.get(simple_url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                img_with_text = add_model_attribution(img, "AI Generated (Fallback)")
                # Clean up the prompt from session state after successful generation
                if 'current_gen_prompt' in st.session_state:
                    del st.session_state.current_gen_prompt
                return img_with_text
        except:
            pass
            
    except Exception as e:
        st.error(f"Image generation failed: {str(e)}")
    
    # Clean up the prompt from session state if generation failed
    if 'current_gen_prompt' in st.session_state:
        del st.session_state.current_gen_prompt
    
    # Return None if all attempts fail
    st.error("Could not generate image after multiple attempts. Please try again.")
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
    Generate image based on selected model.
    """
    
    # Get selected model
    selected_model = st.session_state.get('selected_image_model', 'Auto (Best)')
    
    # Import quiz_config here to avoid circular imports
    from quiz_config import load_quiz_config
    
    # Check if there's a specific prompt in session state (for multi-question support)
    if 'current_gen_prompt' in st.session_state:
        image_prompt = st.session_state.current_gen_prompt
        # Don't delete here - let generate_realistic_fallback handle it
    else:
        # Load prompt from configuration, with detailed fallback
        config = load_quiz_config()
        # For backward compatibility, check if using old format
        if "questions" in config and len(config["questions"]) > 0:
            image_prompt = config["questions"][0].get("image_prompt", "")
        else:
            image_prompt = config.get("image_prompt", "")
    
    # If no prompt is configured or it's empty, use the detailed default
    if not image_prompt or image_prompt.strip() == "":
        image_prompt = """
        Generate a highly realistic, photographic quality image. Style: Professional military documentary photography, 
        Canon 5D Mark IV, 85mm lens, natural lighting, high detail, sharp focus.
        
        Subject: Two young Asian Singaporean male soldiers (NSF, age 19-21) in MODERN Singapore Armed Forces uniforms during route march training.
        
        MODERN SAF UNIFORM DETAILS (Current 2024 standard issue):
        - Modern SAF No.4 digital pixelated camouflage uniform (distinctive green/brown/black pixel pattern)
        - Current SAF Load Bearing Vest (LBV) with MOLLE webbing system
        - Latest model SAF field pack with frame
        - SAF jockey cap with metal Singapore Armed Forces crest badge
        - Black Frontier combat boots (current SAF standard issue)
        - Green SAF admin T-shirt visible at collar
        - Name tag and rank insignia on uniform
        
        Action: Route march injury scenario - one NSF soldier sitting on tarmac road holding injured right ankle 
        with grimacing expression but determined look, second NSF soldier standing beside him bending down 
        to help, showing buddy care system.
        
        Environment: Modern Singapore military training camp (Tekong/Gedong style), SAF buildings with 
        distinctive green metal roofs, covered walkways, tropical trees, hot sunny day with harsh shadows.
        
        Quality: Photorealistic, high resolution, military documentary style, authentic modern SAF context.
        Must look like actual SAF training photograph from 2024, NOT generic military or outdated uniforms.
        """
    
    # Handle Gemini Enhanced option
    if selected_model == "Gemini Enhanced":
        try:
            google_api_key = st.secrets.get("GOOGLE_API_KEY", "")
            if google_api_key and google_api_key != "":
                # Use Gemini to enhance the prompt
                if genai:
                    try:
                        if not NEW_GENAI:
                            # Use old library
                            import google.generativeai as old_genai
                            old_genai.configure(api_key=google_api_key)
                            model = old_genai.GenerativeModel('gemini-pro')
                            
                            enhancement_prompt = f"""
                            Enhance this prompt for maximum photorealism in AI image generation:
                            {image_prompt}
                            
                            Add specific details about lighting, textures, camera settings.
                            Output only the enhanced prompt (150 words max).
                            """
                            
                            response = model.generate_content(enhancement_prompt)
                            enhanced_prompt = response.text.strip()[:500]
                            
                            # Generate with enhanced prompt
                            encoded = urllib.parse.quote(enhanced_prompt)
                            # Don't specify model parameter - use Pollinations default
                            url = f"https://image.pollinations.ai/prompt/{encoded}?width=800&height=400&seed={int(time.time())}"
                            
                            resp = requests.get(url, timeout=60, headers={'User-Agent': 'Mozilla/5.0'})
                            if resp.status_code == 200:
                                img = Image.open(BytesIO(resp.content))
                                # Clean up the prompt from session state after successful generation
                                if 'current_gen_prompt' in st.session_state:
                                    del st.session_state.current_gen_prompt
                                return add_model_attribution(img, "Gemini Enhanced")
                    except Exception as e:
                        st.warning(f"Gemini enhancement failed: {e}. Using standard generation.")
        except:
            pass
    
    # For all other options, use the standard fallback
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