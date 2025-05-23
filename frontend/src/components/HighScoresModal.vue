<template>
  <div v-if="show" class="modal-overlay" @click="close">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2>High Scores</h2>
        <button class="close-btn" @click="close">&times;</button>
      </div>
      <div class="score-list">
        <div v-if="scores.length === 0" class="no-scores">
          No high scores yet!
        </div>
        <div v-else v-for="(score, index) in scores" :key="index" class="score-item">
          <div class="score-rank">{{ index + 1 }}</div>
          <div class="score-details">
            <div class="score-name">{{ score.name }}</div>
            <div class="score-info">
              <span class="score-points">{{ score.score }} points</span>
              <span class="score-words">{{ formatWordCount(score.word_count) }}</span>
              <span class="score-date">{{ formatDate(score.date) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HighScoresModal',
  props: {
    show: {
      type: Boolean,
      required: true
    },
    scores: {
      type: Array,
      default: () => []
    }
  },
  methods: {
    close() {
      this.$emit('close');
    },
    formatDate(dateStr) {
      const date = new Date(dateStr);
      return date.toLocaleDateString();
    },
    formatWordCount(count) {
      return `${count} ${count === 1 ? 'word' : 'words'}`;
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
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
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

.score-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.no-scores {
  text-align: center;
  color: var(--text-color);
  padding: 2rem;
  font-style: italic;
}

.score-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background-color: var(--input-background);
  border-radius: 8px;
  transition: transform 0.2s ease;
}

.score-item:hover {
  transform: translateX(4px);
}

.score-rank {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--primary-color);
  min-width: 2rem;
  text-align: center;
}

.score-details {
  flex: 1;
}

.score-name {
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 0.25rem;
}

.score-info {
  display: flex;
  gap: 1rem;
  font-size: 0.9rem;
  color: var(--text-color);
  opacity: 0.8;
}

.score-points {
  font-weight: 500;
  color: var(--primary-color);
}

.score-words {
  color: var(--text-color);
}

.score-date {
  color: var(--text-color);
  opacity: 0.7;
}
</style> 