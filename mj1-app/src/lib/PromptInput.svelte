<script>
  import { createEventDispatcher } from 'svelte';

  export let value = '';

  const dispatch = createEventDispatcher();

  let suggestions = [
    "Compare the artistic quality and composition of these images",
    "Which image demonstrates better technical execution?",
    "Evaluate based on clarity, color balance, and overall appeal",
    "Judge which image better captures the intended subject",
    "Assess professional quality and production value"
  ];

  let showSuggestions = false;

  function handleFocus() {
    if (value.length === 0) {
      showSuggestions = true;
    }
  }

  function handleBlur() {
    setTimeout(() => showSuggestions = false, 200);
  }

  function selectSuggestion(suggestion) {
    value = suggestion;
    showSuggestions = false;
  }

  function handleKeydown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      showSuggestions = false;
      dispatch('submit');
    }
  }
</script>

<div class="prompt-container">
  <label for="prompt" class="label">Evaluation Criteria</label>
  <textarea
    id="prompt"
    bind:value
    on:focus={handleFocus}
    on:blur={handleBlur}
    on:keydown={handleKeydown}
    placeholder="Describe how you want the images to be compared..."
    rows="4"
    class="textarea"
  ></textarea>

  {#if showSuggestions}
    <div class="suggestions">
      {#each suggestions as suggestion}
        <button
          class="suggestion"
          on:click={() => selectSuggestion(suggestion)}
          type="button"
        >
          {suggestion}
        </button>
      {/each}
    </div>
  {/if}

  <div class="char-count">{value.length} / 1000 characters</div>
</div>

<style>
  .prompt-container {
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

  .suggestions {
    position: absolute;
    top: calc(100% + var(--spacing-sm));
    left: 0;
    right: 0;
    background: var(--color-background);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    overflow: hidden;
    z-index: 10;
    box-shadow: var(--shadow-lg);
  }

  .suggestion {
    display: block;
    width: 100%;
    padding: var(--spacing-md);
    background: transparent;
    color: var(--color-text);
    border: none;
    text-align: left;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 0.875rem;
    line-height: 1.6;
  }

  .suggestion:hover {
    background: var(--color-background-secondary);
    color: var(--color-accent);
  }

  .suggestion + .suggestion {
    border-top: 1px solid var(--color-border);
  }

  .char-count {
    position: absolute;
    bottom: calc(-1.5 * var(--spacing-md));
    right: 0;
    color: var(--color-text-muted);
    font-size: 0.75rem;
  }
</style>