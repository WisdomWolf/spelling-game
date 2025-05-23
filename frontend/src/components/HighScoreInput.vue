<template>
  <div v-if="show" class="modal-overlay">
    <div class="modal-content">
      <div class="modal-header">
        <h2>New High Score!</h2>
        <button class="close-btn" @click="close">&times;</button>
      </div>
      <div class="score-details">
        <div class="score">Score: {{ score }}</div>
        <div class="words">Words: {{ wordCount }}</div>
      </div>
      <form @submit.prevent="submitScore" class="score-form">
        <div class="form-group">
          <label for="name">Enter your name:</label>
          <input
            type="text"
            id="name"
            v-model="name"
            required
            maxlength="20"
            placeholder="Your name"
            ref="nameInput"
          />
        </div>
        <div class="form-actions">
          <button type="submit" :disabled="!name.trim()">Save Score</button>
          <button type="button" class="skip-btn" @click="close">Skip</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HighScoreInput',
  props: {
    show: {
      type: Boolean,
      required: true
    },
    score: {
      type: Number,
      required: true
    },
    wordCount: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      name: ''
    };
  },
  methods: {
    close() {
      this.$emit('close');
    },
    submitScore() {
      if (this.name.trim()) {
        const scoreData = {
          name: this.name.trim(),
          score: this.score,
          wordCount: this.wordCount,
          date: new Date().toISOString()
        };
        this.$emit('submit', scoreData);
        this.close();
      }
    }
  },
  watch: {
    show(newVal) {
      if (newVal) {
        this.$nextTick(() => {
          this.$refs.nameInput?.focus();
        });
      }
    }
  }
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: var(--container-background);
  border-radius: 12px;
  padding: 1.5rem;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 4px 12px var(--shadow-color);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.modal-header h2 {
  margin: 0;
  color: var(--text-color);
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: var(--text-color);
  cursor: pointer;
  padding: 0.5rem;
  line-height: 1;
  border-radius: 50%;
  transition: background-color 0.3s ease;
}

.close-btn:hover {
  background-color: var(--shadow-color);
}

.score-details {
  text-align: center;
  margin-bottom: 1.5rem;
}

.score {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--primary-color);
  margin-bottom: 0.5rem;
}

.words {
  color: var(--text-color);
  opacity: 0.8;
}

.score-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  color: var(--text-color);
  font-weight: 500;
}

.form-group input {
  padding: 0.75rem;
  font-size: 1rem;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  background-color: var(--input-background);
  color: var(--text-color);
  transition: border-color 0.3s ease;
}

.form-group input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.skip-btn {
  background-color: var(--input-background);
  color: var(--text-color);
}

.skip-btn:hover {
  background-color: var(--border-color);
}
</style> 