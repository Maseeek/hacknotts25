import logging
import os
import json
import traceback
from google import genai
from google.genai.errors import APIError
from flask import Flask, request, jsonify, make_response
from dotenv import load_dotenv

# --- Configuration and Initialization ---

# Load environment variables (e.g., from 'info.env')
load_dotenv('info.env')
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Check if API key is loaded
if not GEMINI_API_KEY:
    print("❌ WARNING: GEMINI_API_KEY environment variable is not set! API calls will fail.")
else:
    print("✅ GEMINI API key loaded successfully")

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize the Gemini Client globally
client = None
if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        print("✅ Gemini Client initialized.")
    except Exception as e:
        print(f"❌ Failed to initialize Gemini Client: {e}")
        client = None
else:
    print("❌ Gemini Client not initialized due to missing API Key.")


# --- Prompt Definitions ---

LYRICS_REWRITE_PROMPT = """
You are an expert lyricist, poet, and musical composer with advanced understanding of:
- Songwriting structure and rhythm
- Syllabic and metric alignment
- Rhyme schemes and poetic flow
- Emotional and thematic consistency

## Your Mission
Rewrite existing song lyrics so that they express a new specified theme, while preserving the rhythm, syllable count, rhyme structure, and musical flow of the original lyrics.  
The rewritten lyrics should sound natural when sung to the same melody as the original song.

## Input
Original Lyrics:
{lyrics}

New Theme:
{theme}

## Output Format
Return your result as a **single, valid JSON object** in the following structure. Do not include any text outside the JSON block.

{{
  "theme": "{theme}",
  "rewritten_lyrics": "string (the fully rewritten lyrics, line by line, preserving rhythm and rhyme)",
  "structure_analysis": {{
    "lines_original": number,
    "lines_rewritten": number,
    "syllable_consistency": "high | moderate | low",
    "rhyme_preservation": "strong | partial | minimal"
  }},
  "stylistic_choices": [
    "Short bullet points explaining creative or poetic choices (e.g., metaphor substitutions, tone adjustments, or emotional shifts)"
  ],
  "quality_assurance": [
    "✅ Rewritten lyrics maintain same line structure and flow",
    "✅ Rhyme and syllable pattern preserved where musically appropriate",
    "✅ Theme integrated naturally without forced phrasing",
    "✅ Hooks and choruses remain catchy and emotionally aligned",
    "✅ Output is a valid and complete JSON object only"
  ]
}}

## Style Guidelines
- Keep rhythm and pacing similar to the original
- Preserve emotional intensity and poetic balance
- Avoid overly literal phrasing; use imagery and metaphor
- Do not include explanations or commentary outside of the JSON

STRICT RULE: The entire output must be NOTHING but the valid JSON object.
"""


# --- Utility Functions ---

def _clean_and_parse_json(reply_string: str):
    """Aggressively cleans LLM output and parses it into JSON."""
    json_string = reply_string
            
    # 1. Aggressively strip markdown fences (```json...```)
    if json_string.startswith("```"):
        json_string = json_string.strip().lstrip('```').lstrip('json').strip()
    if json_string.endswith("```"):
        json_string = json_string.rstrip('```').strip()

    # 2. Critical fix for Unterminated String Error: Self-healing JSON
    if not json_string.endswith(('}', ']')):
        last_brace = json_string.rfind('}')
        if last_brace != -1:
            json_string = json_string[:last_brace + 1]
        else:
            raise json.JSONDecodeError("Incomplete JSON structure and cannot self-heal.", json_string, 0)

    # 3. Convert the cleaned JSON string into a Python dictionary
    parsed_response = json.loads(json_string)
    return parsed_response

# --- Middleware and CORS Helpers ---

@app.before_request
def log_request_info():
    print("=" * 50)
    print("🚀 INCOMING REQUEST")
    print(f"📝 Method: {request.method}")
    print(f"🌐 URL: {request.url}")
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            print(f"📦 JSON Data keys: {list(data.keys()) if data else 'None'}")
        except Exception:
            print(f"❌ Could not parse JSON. Raw Data start: {request.get_data()[:50]}...")
    print("=" * 50)

@app.after_request
def log_response_info(response):
    print("=" * 50)
    print("📤 OUTGOING RESPONSE")
    print(f"📊 Status Code: {response.status_code}")
    print("=" * 50)
    return response

def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def _corsify_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

# --- Routes ---

@app.route('/', methods=['GET'])
def home():
    print("🏠 Home route accessed")
    return jsonify({
        "message": "Lyrics API is running!", 
        "status": "ok",
        "api_key_loaded": bool(GEMINI_API_KEY),
        "endpoints": {
            "lyrics": "/lyrics",
            "health": "/health",
            "test": "/test"
        }
    })

@app.route('/test', methods=['GET', 'POST', 'OPTIONS'])
def test():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    
    return _corsify_response(jsonify({
        "message": "Test route working",
        "method": request.method,
    }))

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "services": ["new_lyrics"],
        "api_key_configured": bool(GEMINI_API_KEY)
    })

# Lyrics Generation Route
@app.route('/lyrics', methods=['POST', 'OPTIONS'])
def generate_lyrics():
    print("📝" + "=" * 40)
    print("📝 GENERATE LYRICS ROUTE CALLED")
    
    if request.method == "OPTIONS":
        print("⚡ Handling OPTIONS preflight request")
        return _build_cors_preflight_response()
    
    global client
    if not client:
        print("❌ Gemini Client not available")
        return _corsify_response(jsonify({"error": "Gemini API client not initialized. Check API Key configuration."})), 500
    
    try:
        print("🔍 Starting cover lyrics gen logic...")
        
        data = request.get_json()
        if not data:
            print("❌ No JSON data provided")
            return _corsify_response(jsonify({"error": "No JSON data provided"})), 400
                     
        lyrics = data.get("lyrics")
        theme = data.get("theme")
        if not lyrics or not theme:
            print("❌ Missing lyrics or theme")
            return _corsify_response(jsonify({"error": "Both lyrics and theme are required"})), 400

        prompt = LYRICS_REWRITE_PROMPT.format(lyrics=lyrics, theme=theme)
        
        print("🚀 Sending request to Gemini API...")
        
        try:
            res = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                system_instruction=(
                    "You are an expert lyricist and creative writing assistant. "
                    "Your job is to rewrite given song lyrics so that they align with a specified theme, "
                    "while preserving rhythm, structure, and emotional tone. "
                    "Always respond with a single, valid JSON object following this schema: "
                    '{"theme": "string", "rewritten_lyrics": "string"}. '
                    "Do not include explanations, markdown, or extra text — only the JSON response."
                ),
                    temperature=0.7,
                )
            )
            
        except APIError as e:
            print(f"❌ Gemini API Request Failed: {e}")
            return _corsify_response(jsonify({"error": f"Gemini API call failed: {str(e)}"})), 500
        except Exception as e:
            print(f"❌ General Error during API call: {e}")
            print(f"📋 Traceback: {traceback.format_exc()}")
            return _corsify_response(jsonify({"error": "Internal server error during API call"})), 500

        if res.text is None:
            block_reason = res.candidates[0].finish_reason.name if (res.candidates and res.candidates[0].finish_reason) else "UNKNOWN"
            print(f"❌ Content Blocked or Empty. Reason: {block_reason}")
            
            return _corsify_response(jsonify({
                "error": "AI content generation failed or was blocked.",
                "details": f"Model returned empty content (Finish Reason: {block_reason}). Please review your input.",
                "finish_reason": block_reason
            })), 500

        reply_string = res.text.strip()
        print("✅ Successfully extracted reply string from API")
        
        try:
            parsed_response = _clean_and_parse_json(reply_string)
            print("✅ AI response is valid JSON")
            print("🎉 LYRICS GENERATION SUCCESS")
            
            return _corsify_response(jsonify(parsed_response))
            
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON from AI response: {e}")
            return _corsify_response(jsonify({
                "error": "AI response was not valid JSON despite request.",
                "raw_output_start": reply_string[:200],
                "json_error": str(e)
            })), 500
        
    except Exception as e:
        print("💥" + "=" * 40)
        print("💥 LYRICS GENERATION ERROR")
        print(f"❌ Exception: {str(e)}")
        print(f"📋 Traceback: {traceback.format_exc()}")
        print("💥" + "=" * 40)
        return _corsify_response(jsonify({"error": f"Server error: {str(e)}"})), 500

# --- App Runner ---
if __name__ == "__main__":
    print("🚀 Starting LYRICS Flask app...")
    print(f"🔑 API Key loaded: {bool(GEMINI_API_KEY)}")
    print("📝 Available endpoints:")
    print("  GET  /                      - Home page")
    print("  GET  /health                - Health check")
    print("  POST /lyrics                - new lyrics generation")
    print("  GET/POST /test              - Test endpoint")
    print("---------------------------------------")
    app.run()