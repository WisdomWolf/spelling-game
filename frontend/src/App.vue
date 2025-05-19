<template>
  <div class="container">
    <h1 class="game-title">Spelling Master</h1>

    <!-- Word Input Form -->
    <div v-if="gameState === 'setup'" class="game-container">
      <form @submit.prevent="startGame">
        <div>
          <h2>Add words for spelling practice</h2>
          <div v-for="(word, index) in wordInputs" :key="index" class="word-input-row">
            <input
              type="text"
              v-model="wordInputs[index]"
              placeholder="Enter a word"
              required
              @blur="onInputBlur(index)"
            />
            <button 
              v-if="index > 0" 
              type="button" 
              class="delete-btn" 
              @click="removeWordInput(index)"
              aria-label="Remove word"
            >
              <span aria-hidden="true">×</span>
            </button>
            <!-- Placeholder for alignment on first row -->
            <div v-if="index === 0" class="delete-btn-placeholder"></div>
          </div>
          <div class="form-controls">
            <button type="submit" :disabled="!hasValidWords">Start Game</button>
          </div>
        </div>
      </form>
    </div>

    <!-- Game Screen -->
    <div v-else-if="gameState === 'playing'" class="game-container">
      <div class="score-display">Score: {{ score }}</div>
      
      <div class="attempts">
        <div
          v-for="i in 3"
          :key="i"
          :class="[
            'attempt-indicator',
            { 'current': i === currentAttempt },
            { 'success': i < currentAttempt && lastAttemptSuccess },
            { 'error': i < currentAttempt && !lastAttemptSuccess }
          ]"
        >
          {{ i }}
        </div>
      </div>
      
      <div class="word-display" v-if="showWord">{{ currentWord }}</div>
      <div class="word-display" v-else>🔊</div>
      
      <form @submit.prevent="checkAnswer">
        <input
          type="text"
          v-model="userInput"
          placeholder="Type what you hear"
          ref="answerInput"
          autocomplete="off"
          :disabled="gameState !== 'playing'"
        />
        <div class="form-buttons">
          <button type="button" @click="speakCurrentWord">Hear Word</button>
          <button type="submit">Check</button>
        </div>
      </form>
      
      <div class="feedback" :class="{ 'success': lastAttemptSuccess, 'error': !lastAttemptSuccess && feedback }">
        {{ feedback }}
      </div>
      
      <button v-if="wordsList.length > 0" @click="goToNextWord">Next Word</button>
      <button v-else @click="resetGame">Play Again</button>
    </div>

    <!-- Game Over Screen -->
    <div v-else-if="gameState === 'gameover'" class="game-container">
      <h2>Game Over!</h2>
      <div class="score-display">Final Score: {{ score }}</div>
      <button @click="resetGame">Play Again</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  mounted() {
    console.log('App mounted, audio element ready');
    
    // Test that audio API is working
    setTimeout(() => {
      fetch(`${this.apiBaseUrl}/audio/test?prompt=false`)
        .then(response => {
          if (response.ok) {
            console.log('Audio API test successful');
          } else {
            console.error('Audio API test failed');
          }
        })
        .catch(error => {
          console.error('Error testing audio API:', error);
        });
    }, 1000);
  },
  data() {
    return {
      gameState: 'setup',
      wordInputs: [''],
      wordsList: [],
      currentWord: '',
      userInput: '',
      currentAttempt: 1,
      maxAttempts: 3,
      score: 0,
      feedback: '',
      lastAttemptSuccess: false,
      showWord: false,
      startTime: null,
      apiBaseUrl: 'http://localhost:8000'
    };
  },
  computed: {
    hasValidWords() {
      return this.wordInputs.some(word => word.trim() !== '');
    }
  },
  methods: {
    addWordInput() {
      this.wordInputs.push('');
    },
    
    removeWordInput(index) {
      this.wordInputs.splice(index, 1);
    },
    
    onInputBlur(index) {
      // If this is the last input and it has content, add a new empty input
      if (index === this.wordInputs.length - 1 && this.wordInputs[index].trim() !== '') {
        this.addWordInput();
        
        // Focus the new input after it's added
        this.$nextTick(() => {
          const inputs = document.querySelectorAll('.word-input-row input');
          if (inputs.length > index + 1) {
            inputs[index + 1].focus();
          }
        });
      }
    },
    async startGame() {
      // Filter out empty inputs
      const words = this.wordInputs.filter(word => word.trim() !== '');
      
      if (words.length === 0) {
        alert('Please enter at least one word');
        return;
      }

      try {
        console.log('Starting game with words:', words);
        
        // Send words to backend with timeout
        const response = await axios.post(`${this.apiBaseUrl}/words`, { words }, {
          timeout: 5000 // 5 second timeout
        });
        
        console.log('Backend response:', response.data);
        
        // Initialize the game
        this.wordsList = [...words];
        this.gameState = 'playing';
        this.getNextWord();
      } catch (error) {
        console.error('Error starting game:', error);
        if (error.code === 'ECONNABORTED') {
          alert('Connection to the server timed out. Make sure the backend is running.');
        } else if (error.response) {
          alert(`Server error: ${error.response.data.detail || 'Unknown error'}`);
        } else if (error.request) {
          alert('No response from server. Make sure the backend is running.');
        } else {
          alert(`Failed to start game: ${error.message}`);
        }
      }
    },
    async getNextWord() {
      try {
        console.log('Getting next word...');
        const response = await axios.get(`${this.apiBaseUrl}/word`, {
          timeout: 5000 // 5 second timeout
        });
        
        console.log('Received word:', response.data);
        this.currentWord = response.data.word;
        this.userInput = '';
        this.currentAttempt = 1;
        this.feedback = '';
        this.showWord = false;
        this.startTime = Date.now();
        
        // Remove the word from the list to avoid repetition
        const index = this.wordsList.indexOf(this.currentWord);
        if (index !== -1) {
          this.wordsList.splice(index, 1);
        }
        
        // Focus on the input and speak the word
        this.$nextTick(() => {
          if (this.$refs.answerInput) {
            this.$refs.answerInput.focus();
          }
          this.playWordAudio(true);
        });
      } catch (error) {
        console.error('Error getting word:', error);
        if (error.code === 'ECONNABORTED') {
          alert('Connection to the server timed out. Make sure the backend is running.');
        } else if (error.response) {
          alert(`Server error: ${error.response.data.detail || 'Unknown error'}`);
        } else if (error.request) {
          alert('No response from server. Make sure the backend is running.');
        } else {
          alert(`Failed to get a word: ${error.message}`);
        }
        this.gameState = 'gameover';
      }
    },
    speakCurrentWord() {
      // This is now just a handler for the button click
      this.playWordAudio(true);
    },
    
    playWordAudio(withPrompt = true) {
      console.log('Playing word audio:', this.currentWord);
      
      // Don't show the word when intentionally speaking it
      this.showWord = false;
      
      // Create a new Audio object each time (more reliable than reusing)
      const audio = new Audio();
      
      // Add event listeners
      audio.addEventListener('error', () => {
        console.error('Audio playback error');
        this.showWord = true; // Show the word if audio fails
      });
      
      audio.addEventListener('play', () => {
        console.log('Audio playback started');
      });
      
      audio.addEventListener('ended', () => {
        console.log('Audio playback ended');
      });
      
      // Generate a unique timestamp to prevent caching
      const timestamp = new Date().getTime();
      
      // Set the source
      audio.src = `${this.apiBaseUrl}/audio/${encodeURIComponent(this.currentWord)}?prompt=${withPrompt}&t=${timestamp}`;
      
      // Play the audio
      audio.play().catch(error => {
        console.error('Error playing audio:', error);
        this.showWord = true;
      });
    },
    
    playSuccessSound() {
      try {
        // Create audio context
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (!AudioContext) return;
        
        const audioCtx = new AudioContext();
        
        // Create oscillator for a happy ascending sound
        const oscillator1 = audioCtx.createOscillator();
        const gainNode1 = audioCtx.createGain();
        
        oscillator1.type = 'sine';
        oscillator1.frequency.setValueAtTime(523.25, audioCtx.currentTime); // C5
        oscillator1.frequency.setValueAtTime(659.25, audioCtx.currentTime + 0.1); // E5
        oscillator1.frequency.setValueAtTime(783.99, audioCtx.currentTime + 0.2); // G5
        
        gainNode1.gain.setValueAtTime(0.3, audioCtx.currentTime);
        gainNode1.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.6);
        
        oscillator1.connect(gainNode1);
        gainNode1.connect(audioCtx.destination);
        
        oscillator1.start();
        oscillator1.stop(audioCtx.currentTime + 0.6);
      } catch (error) {
        console.error('Error playing success sound:', error);
      }
    },
    
    playErrorSound() {
      try {
        // Create audio context
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (!AudioContext) return;
        
        const audioCtx = new AudioContext();
        const oscillator = audioCtx.createOscillator();
        const gainNode = audioCtx.createGain();
        
        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(330, audioCtx.currentTime); // E4
        oscillator.frequency.setValueAtTime(220, audioCtx.currentTime + 0.2); // A3
        
        gainNode.gain.setValueAtTime(0.3, audioCtx.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.5);
        
        oscillator.connect(gainNode);
        gainNode.connect(audioCtx.destination);
        
        oscillator.start();
        oscillator.stop(audioCtx.currentTime + 0.5);
      } catch (error) {
        console.error('Error playing error sound:', error);
      }
    },
    checkAnswer() {
      // Normalize answers for comparison (lowercase, trim)
      const normalizedInput = this.userInput.trim().toLowerCase();
      const normalizedWord = this.currentWord.trim().toLowerCase();
      
      if (normalizedInput === normalizedWord) {
        // Calculate score based on attempt number and time
        const timeTaken = (Date.now() - this.startTime) / 1000; // in seconds
        const attemptMultiplier = 4 - this.currentAttempt; // 3 for first, 2 for second, 1 for third
        const timeBonus = Math.max(0, 10 - Math.floor(timeTaken)); // 0-10 points for speed
        const pointsEarned = (10 * attemptMultiplier) + timeBonus;
        
        this.score += pointsEarned;
        this.feedback = `Correct! +${pointsEarned} points`;
        this.lastAttemptSuccess = true;
        
        // Play success sound
        this.playSuccessSound();
        
        // If there are more words, continue, otherwise end the game
        if (this.wordsList.length === 0) {
          setTimeout(() => {
            this.gameState = 'gameover';
          }, 1500);
        } else {
          // Move to next word automatically after delay
          setTimeout(() => {
            this.goToNextWord();
          }, 1500);
        }
      } else {
        this.lastAttemptSuccess = false;
        
        // First increment attempt counter
        this.currentAttempt++;
        
        // Then check if we've reached the maximum
        if (this.currentAttempt > this.maxAttempts) {
          this.feedback = `Sorry, the correct spelling is "${this.currentWord}"`;
          this.showWord = true;
          this.score = Math.max(0, this.score - 5); // Penalty for failing all attempts
        } else {
          this.feedback = `Try again! Attempt ${this.currentAttempt} of ${this.maxAttempts}`;
          this.userInput = '';
          
          // Play error sound and repeat the word
          this.playErrorSound();
          
          setTimeout(() => {
            if (this.$refs.answerInput) {
              this.$refs.answerInput.focus();
            }
            // Speak the word again without the prompt
            setTimeout(() => {
              this.speakCurrentWord(false);
            }, 600);
          }, 500);
        }
      }
    },
    goToNextWord() {
      this.getNextWord();
    },
    resetGame() {
      this.gameState = 'setup';
      this.wordInputs = [''];
      this.wordsList = [];
      this.currentWord = '';
      this.userInput = '';
      this.currentAttempt = 1;
      this.score = 0;
      this.feedback = '';
    }
  }
};
</script>

<style scoped>
.form-controls {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

form {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
}

form button {
  margin-top: 1rem;
}

form button[type="button"] {
  margin-right: 1rem;
}

input {
  margin-bottom: 1.5rem;
}

.form-buttons {
  display: flex;
  justify-content: space-between;
  gap: 1.5rem;
}

.word-input-row {
  display: grid;
  grid-template-columns: 1fr 44px; /* Fixed grid layout: input + button space */
  align-items: center;
  margin-bottom: 0.5rem;
  position: relative;
  width: 100%;
}

.word-input-row input {
  width: 100%;
  margin-bottom: 1rem;
  grid-column: 1;
}

.word-input-row .delete-btn,
.word-input-row .delete-btn-placeholder {
  grid-column: 2;
  justify-self: center;
}

.delete-btn-placeholder {
  width: 36px;
  height: 36px;
  visibility: hidden;
}

.delete-btn {
  background-color: transparent;
  color: #f44336;
  border: none;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  padding: 0;
  margin-left: 8px;
  margin-top: 0;
  font-size: 1.5rem;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.3s;
}

.delete-btn:hover {
  background-color: rgba(244, 67, 54, 0.1);
}

.delete-btn:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(244, 67, 54, 0.2);
}
</style>