from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import random
import os
import tempfile
from typing import List
from gtts import gTTS

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# In-memory storage for words and used words
words = []
used_words = []

class WordList(BaseModel):
    words: List[str]

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
    
    return {"word": random_word}

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)