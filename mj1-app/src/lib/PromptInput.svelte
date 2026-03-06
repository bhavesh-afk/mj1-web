<script>
  import { createEventDispatcher, onMount, onDestroy } from 'svelte';

  export let value = '';

  const dispatch = createEventDispatcher();

  // Animated placeholder prompts
  const prompts = [
    "Which design is more artistic?",
    "Which artwork resembles American Realism the most?",
    "Compare the technical execution and composition",
    "Which image has better color balance and harmony?",
    "Compare the useage of light and shadows"
  ];

  let currentPromptIndex = 0;
  let currentText = '';
  let isTyping = true;
  let typingInterval;
  let pauseTimeout;
  let isFocused = false;

  function typePrompt() {
    if (isFocused || value.length > 0) {
      currentText = '';
      return;
    }

    const targetPrompt = prompts[currentPromptIndex];

    if (currentText.length < targetPrompt.length) {
      currentText = targetPrompt.slice(0, currentText.length + 1);
    } else {
      // Pause at the end of the prompt
      clearInterval(typingInterval);
      pauseTimeout = setTimeout(() => {
        // Clear and move to next prompt
        deletePrompt();
      }, 2000);
    }
  }

  function deletePrompt() {
    typingInterval = setInterval(() => {
      if (currentText.length > 0) {
        currentText = currentText.slice(0, -1);
      } else {
        clearInterval(typingInterval);
        currentPromptIndex = (currentPromptIndex + 1) % prompts.length;
        setTimeout(() => {
          if (!isFocused && value.length === 0) {
            startTyping();
          }
        }, 500);
      }
    }, 30);
  }

  function startTyping() {
    if (isFocused || value.length > 0) return;

    typingInterval = setInterval(typePrompt, 80);
  }

  function handleFocus() {
    isFocused = true;
    currentText = '';
    clearInterval(typingInterval);
    clearTimeout(pauseTimeout);
  }

  function handleBlur() {
    isFocused = false;
    if (value.length === 0) {
      setTimeout(() => {
        if (!isFocused && value.length === 0) {
          startTyping();
        }
      }, 1000);
    }
  }

  function handleKeydown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      dispatch('submit');
    }
  }

  onMount(() => {
    startTyping();
  });

  onDestroy(() => {
    clearInterval(typingInterval);
    clearTimeout(pauseTimeout);
  });
</script>

<div class="prompt-container">
  <label for="prompt" class="label">Evaluation Prompt</label>
  <div class="textarea-wrapper">
    <textarea
      id="prompt"
      bind:value
      on:keydown={handleKeydown}
      on:focus={handleFocus}
      on:blur={handleBlur}
      placeholder=""
      rows="4"
      class="textarea"
    ></textarea>
    {#if !value && !isFocused}
      <div class="animated-placeholder">
        {currentText}<span class="cursor">|</span>
      </div>
    {/if}
  </div>

  <div class="char-count">{value.length} / 1000 characters</div>
</div>

<style>
  .prompt-container {
    position: relative;
  }

  .textarea-wrapper {
    position: relative;
  }

  .label {
    display: block;
    color: var(--color-text);
    font-size: 0.875rem;
    font-weight: 500;
    margin-bottom: var(--spacing-sm);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .textarea {
    width: 100%;
    padding: var(--spacing-md);
    background: var(--color-background-secondary);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    color: var(--color-text);
    font-size: 1rem;
    line-height: 1.6;
    resize: vertical;
    transition: all 0.2s;
    font-family: inherit;
  }

  .textarea:focus {
    outline: none;
    border-color: var(--color-accent);
    background: var(--color-background);
    box-shadow: 0 0 0 3px rgba(45, 127, 130, 0.1);
  }

  .textarea::placeholder {
    color: var(--color-text-muted);
  }

  .animated-placeholder {
    position: absolute;
    top: var(--spacing-md);
    left: var(--spacing-md);
    right: var(--spacing-md);
    color: var(--color-text-muted);
    font-size: 1rem;
    line-height: 1.6;
    pointer-events: none;
    font-family: inherit;
  }

  .cursor {
    display: inline-block;
    animation: blink 1s infinite;
    color: var(--color-accent);
    font-weight: 300;
  }

  @keyframes blink {
    0%, 50% {
      opacity: 1;
    }
    51%, 100% {
      opacity: 0;
    }
  }

  .char-count {
    position: absolute;
    bottom: calc(-1.5 * var(--spacing-md));
    right: 0;
    color: var(--color-text-muted);
    font-size: 0.75rem;
  }
</style>