<template>
  <div class="container">
    <div class="theme-toggle">
      <button 
        class="theme-btn" 
        @click="toggleTheme" 
        :title="isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'"
      >
        {{ isDarkMode ? '🌞' : '🌙' }}
      </button>
    </div>
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
              :required="index === 0"
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
            <div class="start-controls">
              <button type="submit" :disabled="!hasValidWords">Start Game</button>
              <div class="easy-mode-container">
                <label class="easy-mode-toggle">
                  <input type="checkbox" v-model="isEasyMode">
                  <span class="toggle-label">Easy Mode</span>
                  <div class="tooltip">Shows the exact number of letters in the word while guessing</div>
                </label>
              </div>
            </div>
            <div class="secondary-controls">
              <button type="button" class="clear-btn" @click="clearSavedWords">Clear Words</button>
              <button type="button" class="high-scores-btn" @click="showHighScores = true">High Scores</button>
            </div>
          </div>
        </div>
      </form>
    </div>

    <!-- Game Screen -->
    <div v-else-if="gameState === 'playing'" class="game-container">
      <div class="game-header">
        <div class="score-display">Score: {{ score }}</div>
        <button class="exit-btn" @click="exitGame">Exit Game</button>
      </div>
      
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: `${((totalWords - wordsList.length) / totalWords) * 100}%` }"></div>
        <div class="progress-text">Word {{ totalWords - wordsList.length }} of {{ totalWords }}</div>
      </div>
      
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
      
      <div class="word-display-container">
        <div v-if="currentImageUrl" class="word-image">
          <img :src="currentImageUrl" :alt="currentWord" />
        </div>
        <div v-else class="word-display">🔊</div>
      </div>
      
      <form @submit.prevent="checkAnswer" class="letter-form" @keydown="handleKeyPress">
        <LetterInput
          :maxLength="currentWord.length"
          :isDisabled="gameState !== 'playing'"
          :isEasyMode="isEasyMode"
          :correctWord="currentWord"
          @input="handleLetterInput"
          ref="letterInput"
        />
        <div class="form-buttons">
          <button type="button" @click="speakCurrentWord">Hear Word</button>
          <button type="submit">Check Word</button>
        </div>
      </form>
      
      <div class="example-sentence" v-if="currentExampleSentence">
        <p>{{ currentExampleSentence.display }}</p>
        <button 
          @click="speakExampleSentence" 
          :disabled="isAudioPlaying"
          class="hear-sentence-btn"
        >
          <i class="fas fa-volume-up"></i> Hear Sentence
        </button>
      </div>
      
      <div class="feedback" :class="{ 'success': lastAttemptSuccess, 'error': !lastAttemptSuccess && feedback }">
        {{ feedback }}
      </div>
      
      <button v-if="gameState === 'gameover'" @click="resetGame">Play Again</button>
    </div>

    <!-- Game Over Screen -->
    <div v-else-if="gameState === 'gameover'" class="game-container">
      <h2>Game Over!</h2>
      <div class="score-display">Final Score: {{ score }}</div>
      <button @click="resetGame">Play Again</button>
    </div>

    <!-- High Score Components -->
    <HighScoresModal
      :show="showHighScores"
      :scores="highScores"
      @close="showHighScores = false"
    />
    
    <HighScoreInput
      :show="showHighScoreInput"
      :score="score"
      :wordCount="totalWords"
      @close="showHighScoreInput = false"
      @submit="submitHighScore"
    />
  </div>
</template>

<script>
import axios from 'axios';
import LetterInput from './components/LetterInput.vue';
import HighScoresModal from './components/HighScoresModal.vue';
import HighScoreInput from './components/HighScoreInput.vue';

export default {
  name: 'App',
  components: {
    LetterInput,
    HighScoresModal,
    HighScoreInput
  },
  mounted() {
    console.log('App mounted, audio element ready');
    this.applyTheme();
    
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
      wordInputs: [localStorage.getItem('savedWords') ? JSON.parse(localStorage.getItem('savedWords'))[0] || '' : ''],
      wordsList: [],
      totalWords: 0,
      currentWord: '',
      currentImageUrl: null,
      currentExampleSentence: null,
      userInput: '',
      currentAttempt: 1,
      maxAttempts: 3,
      score: 0,
      feedback: '',
      lastAttemptSuccess: false,
      showWord: false,
      startTime: null,
      apiBaseUrl: 'http://localhost:8000',
      isEasyMode: false,
      isDarkMode: localStorage.getItem('darkMode') === 'true',
      isAudioPlaying: false,
      showHighScores: false,
      showHighScoreInput: false,
      highScores: [],
      isNewHighScore: false
    };
  },
  computed: {
    hasValidWords() {
      return this.wordInputs.some(word => word.trim() !== '');
    },
    savedWords() {
      return localStorage.getItem('savedWords') ? JSON.parse(localStorage.getItem('savedWords')) : [];
    }
  },
  methods: {
    toggleTheme() {
      this.isDarkMode = !this.isDarkMode;
      localStorage.setItem('darkMode', this.isDarkMode);
      this.applyTheme();
    },
    applyTheme() {
      document.documentElement.setAttribute('data-theme', this.isDarkMode ? 'dark' : 'light');
    },
    addWordInput() {
      this.wordInputs.push('');
    },
    
    removeWordInput(index) {
      this.wordInputs.splice(index, 1);
      this.saveWords();
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
      this.saveWords();
    },

    saveWords() {
      const validWords = this.wordInputs.filter(word => word.trim() !== '');
      localStorage.setItem('savedWords', JSON.stringify(validWords));
    },

    clearSavedWords() {
      if (confirm('Are you sure you want to clear all saved words?')) {
        localStorage.removeItem('savedWords');
        this.wordInputs = [''];
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
        this.totalWords = words.length;
        this.gameState = 'playing';
        this.getNextWord();
        await this.loadHighScores();
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
        this.currentImageUrl = response.data.image_url;
        this.currentExampleSentence = response.data.example_sentence;
        this.userInput = '';
        this.currentAttempt = 1;
        this.feedback = '';
        this.showWord = false;
        this.startTime = Date.now();
        
        // Clear the letter input
        this.$nextTick(() => {
          if (this.$refs.letterInput) {
            console.log('Clearing letter input');
            this.$refs.letterInput.clear();
            this.$refs.letterInput.focus();
          }
          this.playWordAudio(true);
        });
        
        // Remove the word from the list to avoid repetition
        const index = this.wordsList.indexOf(this.currentWord);
        if (index !== -1) {
          this.wordsList.splice(index, 1);
        }
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
      // Refocus the input after clicking the button
      this.$nextTick(() => {
        if (this.$refs.letterInput) {
          this.$refs.letterInput.focus();
        }
      });
    },
    
    playWordAudio(withPrompt = true) {
      console.log('Playing word audio:', this.currentWord);
      
      // Don't show the word when intentionally speaking it
      this.showWord = false;
      
      // If audio is already playing, ignore the request
      if (this.isAudioPlaying) {
        console.log('Audio already playing, ignoring request');
        return;
      }
      
      // Create a new Audio object each time (more reliable than reusing)
      const audio = new Audio();
      
      // Add event listeners
      audio.addEventListener('error', () => {
        console.error('Audio playback error');
        this.showWord = true; // Show the word if audio fails
        this.isAudioPlaying = false;
      });
      
      audio.addEventListener('play', () => {
        console.log('Audio playback started');
        this.isAudioPlaying = true;
      });
      
      audio.addEventListener('ended', () => {
        console.log('Audio playback ended');
        this.isAudioPlaying = false;
      });
      
      // Generate a unique timestamp to prevent caching
      const timestamp = new Date().getTime();
      
      // Set the source
      audio.src = `${this.apiBaseUrl}/audio/${encodeURIComponent(this.currentWord)}?prompt=${withPrompt}&t=${timestamp}`;
      
      // Play the audio
      audio.play().catch(error => {
        console.error('Error playing audio:', error);
        this.showWord = true;
        this.isAudioPlaying = false;
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
            this.checkIfHighScore();
          }, 1500);
        } else {
          // Move to next word automatically after delay
          setTimeout(() => {
            this.getNextWord();
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
          
          // Move to next word automatically after delay
          setTimeout(() => {
            if (this.wordsList.length > 0) {
              this.getNextWord();
            } else {
              this.gameState = 'gameover';
              this.checkIfHighScore();
            }
          }, 2000);
        } else {
          this.feedback = `Try again! Attempt ${this.currentAttempt} of ${this.maxAttempts}`;
          
          // Show incorrect letters in easy mode before clearing
          if (this.$refs.letterInput) {
            this.$refs.letterInput.showIncorrectLetters();
          }
          
          // Play error sound and repeat the word
          this.playErrorSound();
          
          setTimeout(() => {
            if (this.$refs.letterInput) {
              this.$refs.letterInput.focus();
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
    async resetGame() {
      this.gameState = 'setup';
      // Don't clear wordInputs here to preserve the list
      this.wordsList = [];
      this.currentWord = '';
      this.userInput = '';
      this.currentAttempt = 1;
      this.score = 0;
      this.feedback = '';
      this.isNewHighScore = false;
      await this.loadHighScores();
    },
    exitGame() {
      if (confirm('Are you sure you want to exit the game? Your progress will be lost.')) {
        this.resetGame();
      }
    },
    handleLetterInput(value) {
      console.log('Letter input received:', value);
      this.userInput = value;
    },
    handleKeyPress(event) {
      if (event.key === 'Enter' && this.gameState === 'playing') {
        this.checkAnswer();
      }
    },
    async loadHighScores() {
      try {
        console.log('Loading high scores...');
        const response = await axios.get(`${this.apiBaseUrl}/high-scores`);
        console.log('High scores loaded:', response.data.scores);
        this.highScores = response.data.scores;
      } catch (error) {
        console.error('Error loading high scores:', error);
        this.highScores = [];
      }
    },
    
    async submitHighScore(scoreData) {
      try {
        // Transform the data to match the backend model exactly
        const transformedData = {
          name: scoreData.name.trim(),
          score: parseInt(scoreData.score),
          word_count: parseInt(scoreData.wordCount),
          date: new Date().toISOString()
        };
        
        console.log('Submitting high score:', transformedData);
        const response = await axios.post(`${this.apiBaseUrl}/high-scores`, transformedData);
        console.log('High score submission response:', response.data);
        
        // Show success feedback
        this.feedback = 'High score saved!';
        this.lastAttemptSuccess = true;
        
        // Reload high scores
        await this.loadHighScores();
        
        // Close the input modal and show high scores
        this.showHighScoreInput = false;
        this.showHighScores = true;
        
        // Return to start screen after a short delay
        setTimeout(() => {
          this.resetGame();
        }, 2000);
      } catch (error) {
        console.error('Error submitting high score:', error);
        this.feedback = 'Failed to save high score. Please try again.';
        this.lastAttemptSuccess = false;
      }
    },
    
    checkIfHighScore() {
      if (this.highScores.length < 10 || this.score > this.highScores[this.highScores.length - 1].score) {
        console.log('New high score achieved!');
        this.isNewHighScore = true;
        this.showHighScoreInput = true;
      } else {
        console.log('Not a high score');
      }
    },
    async speakExampleSentence() {
      if (!this.currentExampleSentence?.audio || this.isAudioPlaying) return;
      
      // Refocus input immediately after clicking the button
      this.$nextTick(() => {
        if (this.$refs.letterInput) {
          this.$refs.letterInput.focus();
        }
      });
      
      try {
        console.log('Fetching audio for example sentence:', this.currentExampleSentence.audio);
        const audio = new Audio(`${this.apiBaseUrl}/audio/${encodeURIComponent(this.currentExampleSentence.audio)}?prompt=false`);
        
        audio.addEventListener('error', (e) => {
          console.error('Error playing audio:', e);
          this.isAudioPlaying = false;
        });
        
        audio.addEventListener('play', () => {
          console.log('Audio playback started');
          this.isAudioPlaying = true;
        });
        
        audio.addEventListener('ended', () => {
          console.log('Audio playback ended');
          this.isAudioPlaying = false;
        });
        
        await audio.play();
      } catch (error) {
        console.error('Error playing example sentence:', error);
        this.isAudioPlaying = false;
      }
    }
  }
};
</script>

<style scoped>
.container {
  max-width: 100%;
  padding: 2rem;
  margin: 0 auto;
}

.game-container {
  width: 100%;
  max-width: 100%;
  margin: 0 auto;
  padding: 1rem;
}

form {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 100%;
  margin: 0 auto;
}

.letter-form {
  width: 100%;
  max-width: 100%;
  margin: 0 auto;
}

.form-controls {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-top: 1rem;
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

.start-controls {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.easy-mode-container {
  margin: 0;
  text-align: center;
}

.easy-mode-toggle {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  user-select: none;
  position: relative;
  padding: 0.5rem;
  border-radius: 8px;
  transition: background-color 0.3s ease;
}

.easy-mode-toggle:hover {
  background-color: var(--shadow-color);
}

.easy-mode-toggle input[type="checkbox"] {
  margin: 0;
  cursor: pointer;
  width: 20px;
  height: 20px;
  accent-color: var(--primary-color);
}

.toggle-label {
  font-size: 1rem;
  color: var(--text-color);
  font-weight: 500;
}

.tooltip {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%) translateY(10px);
  padding: 0.5rem;
  background-color: var(--container-background);
  color: var(--text-color);
  text-align: center;
  border-radius: 4px;
  font-size: 0.8rem;
  white-space: nowrap;
  margin-bottom: 0.5rem;
  z-index: 1;
  box-shadow: 0 2px 8px var(--shadow-color);
  border: 1px solid var(--border-color);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.tooltip::after {
  content: "";
  position: absolute;
  top: 100%;
  left: 50%;
  margin-left: -5px;
  border-width: 5px;
  border-style: solid;
  border-color: var(--border-color) transparent transparent transparent;
}

.easy-mode-toggle:hover .tooltip {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
  transition-delay: 0.3s;
}

.theme-toggle {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 1000;
}

.theme-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.3s ease;
}

.theme-btn:hover {
  background-color: var(--shadow-color);
}

.secondary-controls {
  display: flex;
  gap: 1rem;
}

.high-scores-btn {
  background-color: var(--secondary-color);
}

.high-scores-btn:hover {
  background-color: var(--primary-color);
}

.word-display-container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 2rem 0;
  min-height: 200px;
  max-height: 300px;
  width: 100%;
}

.word-image {
  max-width: 100%;
  max-height: 300px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px var(--shadow-color);
  display: flex;
  justify-content: center;
  align-items: center;
}

.word-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  max-height: 300px;
}

.example-sentence {
  margin: 1.5rem 0;
  padding: 1rem;
  background-color: var(--input-background);
  border-radius: 8px;
  text-align: center;
}

.example-sentence p {
  margin: 0 0 1rem 0;
  font-style: italic;
  color: var(--text-color);
}

.hear-sentence-btn {
  background-color: var(--secondary-color);
  color: var(--text-color);
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.hear-sentence-btn:hover:not(:disabled) {
  background-color: var(--primary-color);
}

.hear-sentence-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>