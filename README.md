# Spelling Game

A fun spelling game web application designed to help elementary school children practice their spelling skills.

## Features

- Input custom spelling words
- Text-to-speech word pronunciation
- Child-friendly, colorful user interface
- Scoring system with bonuses for speed and accuracy
- Three attempts per word
- Progress tracking with visual feedback

## Technology Stack

- **Backend**: Python with FastAPI and Poetry
- **Frontend**: Vue 3 with Vite

## Setup Instructions

### Backend

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Install dependencies using Poetry:
   ```
   poetry install
   ```

3. Run the backend server:
   ```
   poetry run python main.py
   ```

   The backend server will run on http://localhost:8000

### Frontend

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Run the development server:
   ```
   npm run dev
   ```

   The frontend will be available at http://localhost:3000

## How to Play

1. Enter your spelling words in the setup screen
2. Click "Start Game" to begin
3. Listen to the word pronunciation (click "Hear Word" to replay)
4. Type your answer and press Enter or click "Check"
5. You have three attempts per word
6. Earn more points for faster, correct answers on early attempts
7. Continue until all words are completed

## License

MIT