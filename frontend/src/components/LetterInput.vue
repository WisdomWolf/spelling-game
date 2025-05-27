<template>
  <div 
    class="letter-input-container" 
    tabindex="0" 
    @keydown="handleKeyPress"
    @click="focus"
  >
    <div class="letter-slots">
      <template v-if="isEasyMode">
        <div 
          v-for="(letter, index) in letterSlots" 
          :key="index"
          class="letter-slot"
          :class="{ 
            'filled': letter !== '',
            'incorrect': showIncorrect && letter !== '' && letter !== correctWord[index]
          }"
        >
          <svg 
            v-if="letter !== ''"
            class="letter-svg"
            viewBox="0 0 100 100"
            xmlns="http://www.w3.org/2000/svg"
          >
            <text
              x="50"
              y="70"
              text-anchor="middle"
              class="letter-text"
            >{{ letter.toUpperCase() }}</text>
          </svg>
        </div>
      </template>
      <template v-else>
        <div 
          v-for="(letter, index) in currentLetters" 
          :key="index"
          class="letter-slot"
          :class="{ 'filled': letter !== '' }"
        >
          <svg 
            v-if="letter !== ''"
            class="letter-svg"
            viewBox="0 0 100 100"
            xmlns="http://www.w3.org/2000/svg"
          >
            <text
              x="50"
              y="70"
              text-anchor="middle"
              class="letter-text"
            >{{ letter.toUpperCase() }}</text>
          </svg>
        </div>
        <div 
          class="letter-slot active"
        >
          <div class="cursor"></div>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LetterInput',
  props: {
    maxLength: {
      type: Number,
      required: true,
      validator: value => value > 0 && value <= 20
    },
    isDisabled: {
      type: Boolean,
      default: false
    },
    isEasyMode: {
      type: Boolean,
      default: false
    },
    correctWord: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      currentLetters: [],
      letterSlots: Array(this.maxLength).fill(''),
      showIncorrect: false
    }
  },
  mounted() {
    console.log('LetterInput mounted, maxLength:', this.maxLength);
    this.focus();
  },
  beforeUnmount() {
    document.removeEventListener('keydown', this.handleKeyPress);
  },
  watch: {
    isDisabled(newValue) {
      if (newValue) {
        document.removeEventListener('keydown', this.handleKeyPress);
      } else {
        document.addEventListener('keydown', this.handleKeyPress);
      }
    },
    maxLength(newLength) {
      // Ensure maxLength is between 1 and 20
      const validLength = Math.min(Math.max(newLength, 1), 20);
      this.letterSlots = Array(validLength).fill('');
    }
  },
  methods: {
    handleKeyPress(event) {
      console.log('Key pressed:', event.key);
      if (this.isDisabled) {
        console.log('Component is disabled');
        return;
      }

      if (event.key === 'Backspace') {
        console.log('Handling backspace');
        this.handleBackspace();
        event.preventDefault();
      } else if (/^[a-zA-Z]$/.test(event.key)) {
        console.log('Handling letter:', event.key);
        if (this.isEasyMode) {
          const emptySlotIndex = this.letterSlots.findIndex(slot => slot === '');
          if (emptySlotIndex !== -1) {
            this.letterSlots[emptySlotIndex] = event.key.toLowerCase();
            this.$emit('input', this.letterSlots.join(''));
          }
        } else {
          // In normal mode, only limit to 20 characters
          if (this.currentLetters.length >= 20) {
            console.log('Maximum length reached (20 characters)');
            return;
          }
          this.currentLetters.push(event.key.toLowerCase());
          this.$emit('input', this.currentLetters.join(''));
        }
        event.preventDefault();
      }
    },
    handleBackspace() {
      if (this.isEasyMode) {
        const lastFilledIndex = [...this.letterSlots].reverse().findIndex(slot => slot !== '');
        if (lastFilledIndex !== -1) {
          const index = this.letterSlots.length - 1 - lastFilledIndex;
          this.letterSlots[index] = '';
          this.$emit('input', this.letterSlots.join(''));
        }
      } else {
        if (this.currentLetters.length > 0) {
          this.currentLetters.pop();
          this.$emit('input', this.currentLetters.join(''));
        }
      }
    },
    clear() {
      if (this.isEasyMode) {
        this.letterSlots = Array(this.maxLength).fill('');
      } else {
        this.currentLetters = [];
      }
      this.$emit('input', '');
      console.log('Cleared letters');
      this.$nextTick(() => {
        this.focus();
      });
    },
    showIncorrectLetters() {
      if (this.isEasyMode) {
        this.showIncorrect = true;
        setTimeout(() => {
          this.showIncorrect = false;
          this.clear();
        }, 1000);
      } else {
        this.clear();
      }
    },
    focus() {
      console.log('Focusing letter input');
      this.$el.focus();
    }
  }
}
</script>

<style scoped>
.letter-input-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  margin: 0 auto;
  outline: none;
  cursor: text;
}

.letter-slots {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 1rem;
  min-height: 80px;
  flex-wrap: wrap;
  width: 100%;
  padding: 0;
}

.letter-slot {
  width: 60px;
  height: 80px;
  border: 3px solid var(--secondary-color);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: white;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.letter-slot.filled {
  background-color: var(--secondary-color);
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(33, 150, 243, 0.3);
}

.letter-slot.active {
  border-style: dashed;
  animation: pulse 1.5s infinite;
}

.cursor {
  width: 4px;
  height: 40px;
  background-color: var(--secondary-color);
  animation: blink 1s infinite;
}

.letter-svg {
  width: 100%;
  height: 100%;
}

.letter-text {
  font-family: 'Comic Neue', cursive;
  font-size: min(48px, 6vw);
  fill: white;
  font-weight: bold;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

@media (max-width: 600px) {
  .letter-slot {
    width: 45px;
    height: 60px;
  }
  
  .letter-text {
    font-size: 36px;
  }
}

.letter-slot.incorrect {
  background-color: var(--error-color);
  animation: shake 0.5s;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}
</style> 