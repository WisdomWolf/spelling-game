from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import random
import os
import tempfile
from typing import List, Optional
from gtts import gTTS
import json
from datetime import datetime
import requests
from dotenv import load_dotenv
import argparse

# Load environment variables
load_dotenv()

# Parse command line arguments
parser = argparse.ArgumentParser(description='Spelling Game Backend')
parser.add_argument('--enable-images', action='store_true', help='Enable image fetching')
# Allow unknown arguments to pass through to uvicorn
args, unknown = parser.parse_known_args()

# Image fetching configuration
ENABLE_IMAGES = os.getenv('ENABLE_IMAGES', 'false').lower() == 'true' or args.enable_images

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Image API configuration
IMAGE_API_URL = "https://placehold.co/800x600/2563eb/ffffff"

# Free Dictionary API URL
DICTIONARY_API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"

# Unsplash API configuration
UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"
UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY')  # This is your Client ID/Access Key

# In-memory storage for words and used words
words = []
used_words = []

# Initialize game state
game_state = {
    "words": [],
    "current_word_index": 0
}

# High scores file path
HIGH_SCORES_FILE = "high_scores.json"

class WordList(BaseModel):
    words: List[str]

class HighScore(BaseModel):
    name: str
    score: int
    date: str
    word_count: int

def load_high_scores():
    if os.path.exists(HIGH_SCORES_FILE):
        with open(HIGH_SCORES_FILE, 'r') as f:
            return json.load(f)
    return []

def save_high_scores(scores):
    with open(HIGH_SCORES_FILE, 'w') as f:
        json.dump(scores, f)

async def get_word_image(word: str) -> Optional[str]:
    """Fetch an image URL for the given word using Unsplash API."""
    if not ENABLE_IMAGES:
        print("Image fetching is disabled")
        return None
        
    try:
        print(f"\nFetching image for word: {word}")
        
        if not UNSPLASH_ACCESS_KEY:
            print("No Unsplash Access Key found. Please set UNSPLASH_ACCESS_KEY in your .env file")
            return None
        
        # Use a simple search query
        params = {
            "query": word,
            "per_page": 1,
            "orientation": "landscape"
        }
        
        # Make the request
        response = requests.get(
            UNSPLASH_API_URL,
            params=params,
            headers={
                "Accept-Version": "v1",
                "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
            }
        )
        
        print(f"Unsplash API response status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("results") and len(data["results"]) > 0:
                # Use the small size URL instead of regular
                image_url = data["results"][0]["urls"]["small"]
                print(f"Found image URL: {image_url}")
                return image_url
            print("No images found in response")
        else:
            print(f"Error response from Unsplash: {response.text}")
            
        return None
    except Exception as e:
        print(f"Error fetching image for {word}: {str(e)}")
        return None

async def get_example_sentence(word: str) -> Optional[dict]:
    """Get an example sentence from the Free Dictionary API and return both masked and unmasked versions."""
    try:
        response = requests.get(f"{DICTIONARY_API_URL}{word}")
        response.raise_for_status()
        
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            # Look for example sentences in the definitions
            for meaning in data[0].get('meanings', []):
                for definition in meaning.get('definitions', []):
                    if 'example' in definition:
                        example = definition['example']
                        # Remove any quotes and ensure it ends with a period
                        example = example.strip('"\'')
                        if not example.endswith('.'):
                            example += '.'
                        # Create masked version
                        masked_example = example.replace(word, '____')
                        return {
                            "display": masked_example,
                            "audio": example
                        }
            
            # If no example found, use the first definition as a fallback
            for meaning in data[0].get('meanings', []):
                for definition in meaning.get('definitions', []):
                    if 'definition' in definition:
                        display = f"The word '____' means: {definition['definition']}."
                        audio = f"The word '{word}' means: {definition['definition']}."
                        return {
                            "display": display,
                            "audio": audio
                        }
        
        return None
    except Exception as e:
        print(f"Error fetching example sentence for {word}: {e}")
        return None

@app.post("/words")
async def add_words(word_list: WordList):
    global words, used_words
    words = word_list.words
    used_words = []
    return {"status": "success", "word_count": len(words)}

@app.get("/word")
async def get_random_word():
    global words, used_words
    
    if not words:
        raise HTTPException(status_code=404, detail="No words available")
    
    # If all words have been used, reset
    if len(used_words) == len(words):
        used_words = []
    
    # Get available words (ones we haven't used yet)
    available_words = [word for word in words if word not in used_words]
    
    if not available_words:
        raise HTTPException(status_code=404, detail="No words available")
    
    # Select a random word
    random_word = random.choice(available_words)
    used_words.append(random_word)
    
    # Get additional data for the word
    image_url = await get_word_image(random_word)
    example_sentence = await get_example_sentence(random_word)
    
    return {
        "word": random_word,
        "image_url": image_url,
        "example_sentence": example_sentence
    }

@app.get("/audio/{text}")
async def get_audio(text: str, prompt: bool = True, t: str = None):
    """Generate audio for a word or phrase
    
    t parameter is used to prevent browser caching
    """
    try:
        print(f"Generating audio for word: '{text}' with prompt={prompt}")
        
        # Create a temporary file to store the audio
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_filename = temp_file.name
        temp_file.close()
        
        # Generate the text to speak
        if prompt and text != "test":
            speech_text = f"Your word is... {text}"
        else:
            speech_text = text
            
        print(f"Speech text: '{speech_text}'")
            
        # Generate audio file using gTTS
        tts = gTTS(speech_text, lang="en", slow=False)
        tts.save(temp_filename)
        
        # Return the audio file
        headers = {
            "Content-Disposition": f"attachment; filename={text}.mp3",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
        
        print(f"Sending audio file: {temp_filename}")
        
        return FileResponse(
            temp_filename, 
            headers=headers, 
            media_type="audio/mpeg",
            background=None  # Ensure synchronous response
        )
    except Exception as e:
        print(f"Error generating audio: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate audio: {str(e)}")

@app.post("/high-scores")
async def add_high_score(score: HighScore):
    scores = load_high_scores()
    scores.append(score.dict())
    # Sort by score in descending order
    scores.sort(key=lambda x: x['score'], reverse=True)
    # Keep only top 10 scores
    scores = scores[:10]
    save_high_scores(scores)
    return {"message": "High score added successfully"}

@app.get("/high-scores")
async def get_high_scores():
    scores = load_high_scores()
    return {"scores": scores}

@app.get("/config")
async def get_config():
    """Return the current configuration."""
    return {
        "enable_images": ENABLE_IMAGES
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)