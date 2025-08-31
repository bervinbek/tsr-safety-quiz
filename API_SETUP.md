# Image Generation API Setup

This application uses AI to generate realistic safety scenario images. 

## Primary: Google Gemini 2.0 Flash (Optional)

To use Google Gemini for enhanced image generation:

1. **Get a FREE Google API Key:**
   - Go to https://aistudio.google.com/apikey
   - Click "Create API Key"
   - Copy your key

2. **Add to `.streamlit/secrets.toml`:**
   ```toml
   GOOGLE_API_KEY = "your-google-api-key-here"
   ```

3. **Benefits:**
   - Uses Gemini 2.0 Flash to enhance prompts
   - Better understanding of SAF context
   - More accurate military details
   - Free tier: 15 requests/minute, 1 million tokens/month

## Current Implementation (Works Without API Key!)

If no Google API key is provided, the app uses:

1. **Pollinations AI** (Default)
   - ✅ Completely FREE
   - ✅ No API key needed
   - ✅ High-quality image generation
   - Uses Flux model

2. **Hugging Face** (Backup)
   - Your token is already configured
   - Faster generation with Stable Diffusion

3. **Custom Illustration** (Fallback)
   - Always available
   - Instant generation

## Optional: Additional Services

If you want even more options, you can add:

### Replicate (Free tier available)
1. Go to https://replicate.com
2. Create free account
3. Get API token from settings
4. Add to `.streamlit/secrets.toml`:
   ```toml
   REPLICATE_API_TOKEN = "your-token"
   ```

### Stability AI (Paid service)
- Professional quality
- Visit https://platform.stability.ai
- Requires payment

## No Action Needed!

The app already works perfectly with the free Pollinations AI service. Just click the regenerate button (🔄) on the quiz page if you want a different image.