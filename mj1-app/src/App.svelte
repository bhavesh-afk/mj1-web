<script>
  import './app.css';
  import Logo from './lib/Logo.svelte';
  import ImageUploader from './lib/ImageUploader.svelte';
  import MultiImageUploader from './lib/MultiImageUploader.svelte';
  import PromptInput from './lib/PromptInput.svelte';
  import ResultDisplay from './lib/ResultDisplay.svelte';
  import LoadingScreen from './lib/LoadingScreen.svelte';

  let imagesA = [];
  let imagesB = [];
  let promptImages = [];
  let imageA = null;  // For single image mode
  let imageB = null;  // For single image mode
  let prompt = '';
  let isJudging = false;
  let judgment = null;
  let temperature = 0.0;
  let maxTokens = 2048;
  let useMultipleImages = false;

  async function handleJudge() {
    const hasImageA = useMultipleImages ? imagesA.length > 0 : imageA;
    const hasImageB = useMultipleImages ? imagesB.length > 0 : imageB;

    if (!hasImageA || !hasImageB || !prompt) {
      return;
    }

    isJudging = true;

    try {
      // Import the secure API module
      const { judgeImages } = await import('./lib/api.js');

      // Get the images to send
      const imageToSendA = useMultipleImages ? imagesA[0] : imageA;
      const imageToSendB = useMultipleImages ? imagesB[0] : imageB;

      // Call the secure API function
      judgment = await judgeImages(
        imageToSendA,
        imageToSendB,
        prompt,
        temperature,
        maxTokens
      );
    } catch (error) {
      console.error('Error:', error.message);

      // Show user-friendly error message
      alert(error.message || 'Failed to generate judgment. Please try again.');

      // Don't set fallback judgment on error
      judgment = null;
    } finally {
      isJudging = false;
    }
  }

  function reset() {
    imageA = null;
    imageB = null;
    imagesA = [];
    imagesB = [];
    promptImages = [];
    prompt = '';
    judgment = null;
  }
</script>

<main>
  <!-- Navigation -->
  <nav class="nav">
    <div class="nav-container">
      <button class="nav-brand" on:click={reset}>
        <Logo />
        <span class="brand-text">MJ1</span>
      </button>
      <div class="nav-subtitle">MultiModal Judge</div>
    </div>
  </nav>

  <!-- Main Content -->
  <div class="container">
    {#if !judgment}
      <!-- Hero Section -->
      <section class="hero">
        <h1 class="hero-title">King of Taste</h1>
        <p class="hero-description">
          SOTA Multi-Modal Judge on human preference judgement
        </p>
      </section>

      <!-- Upload Section -->
      <section class="upload-section">
        <div class="upload-grid">
          {#if useMultipleImages}
            <MultiImageUploader
              label="Images A"
              bind:images={imagesA}
              maxImages={5}
            />
            <div class="divider">
              <span class="divider-text">vs</span>
            </div>
            <MultiImageUploader
              label="Images B"
              bind:images={imagesB}
              maxImages={5}
            />
          {:else}
            <ImageUploader
              label="Image A"
              bind:image={imageA}
            />
            <div class="divider">
              <span class="divider-text">vs</span>
            </div>
            <ImageUploader
              label="Image B"
              bind:image={imageB}
            />
          {/if}
        </div>
      </section>

      <!-- Prompt Section -->
      <section class="prompt-section">
        <PromptInput bind:value={prompt} on:submit={handleJudge} />
      </section>

      <!-- Parameters Section -->
      <section class="parameters">
        <details class="parameters-details">
          <summary class="parameters-summary">Advanced Parameters</summary>
          <div class="parameters-grid">
            <div class="parameter">
              <label for="temperature">Temperature: {temperature}</label>
              <input
                id="temperature"
                type="range"
                min="0"
                max="1"
                step="0.1"
                bind:value={temperature}
              />
            </div>
            <div class="parameter">
              <label for="maxTokens">Max Tokens: {maxTokens}</label>
              <input
                id="maxTokens"
                type="number"
                min="100"
                max="4096"
                bind:value={maxTokens}
              />
            </div>
            <div class="parameter full-width">
              <label for="multipleImages">
                <input
                  id="multipleImages"
                  type="checkbox"
                  bind:checked={useMultipleImages}
                />
                Enable Multiple Images
              </label>
            </div>
          </div>

          <!-- Prompt Images Section -->
          <div class="prompt-images-section">
            <h4 class="section-title">Prompt Images (Optional)</h4>
            <p class="section-description">Add reference images to provide additional context for your judgment criteria</p>
            <MultiImageUploader
              label="Prompt Images"
              bind:images={promptImages}
              maxImages={3}
            />
          </div>
        </details>
      </section>

      <!-- Action Button -->
      <section class="actions">
        <button
          class="btn-primary"
          on:click={handleJudge}
          disabled={(useMultipleImages ? (imagesA.length === 0 || imagesB.length === 0) : (!imageA || !imageB)) || !prompt || isJudging}
        >
          Generate Judgment
        </button>
      </section>
    {:else}
      <!-- Results Section -->
      <section class="results">
        <ResultDisplay
          {judgment}
          imageA={useMultipleImages && imagesA.length > 0 ? imagesA[0] : imageA}
          imageB={useMultipleImages && imagesB.length > 0 ? imagesB[0] : imageB}
        />
        <div class="results-actions">
          <button class="btn-secondary" on:click={reset}>
            New Comparison
          </button>
          <span class="hint">Or click the MJ1 logo to start over</span>
        </div>
      </section>
    {/if}
  </div>

  <!-- Loading Screen Overlay -->
  <LoadingScreen isLoading={isJudging} />
</main>

<style>
  main {
    min-height: 100vh;
    background: var(--color-background);
  }

  .nav {
    border-bottom: 1px solid var(--color-border);
    background: var(--color-background);
    position: sticky;
    top: 0;
    z-index: 100;
    backdrop-filter: blur(8px);
  }

  .nav-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: var(--spacing-lg) var(--spacing-xl);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .nav-brand {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    background: transparent;
    border: none;
    cursor: pointer;
    padding: 0;
    transition: opacity 0.2s;
  }

  .nav-brand:hover {
    opacity: 0.8;
  }

  .brand-text {
    font-size: 1.75rem;
    font-weight: 300;
    letter-spacing: -0.5px;
    color: var(--color-text);
  }

  .nav-subtitle {
    color: var(--color-text-muted);
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: var(--spacing-2xl) var(--spacing-xl);
  }

  .hero {
    text-align: center;
    margin-bottom: var(--spacing-2xl);
  }

  .hero-title {
    font-size: 2.5rem;
    font-weight: 300;
    margin-bottom: var(--spacing-md);
    color: var(--color-text);
  }

  .hero-description {
    font-size: 1.125rem;
    color: var(--color-text-muted);
    max-width: 600px;
    margin: 0 auto;
  }

  .upload-section {
    margin-bottom: var(--spacing-2xl);
  }

  .upload-grid {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    gap: var(--spacing-xl);
    align-items: stretch;
  }

  .divider {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 var(--spacing-lg);
  }

  .divider-text {
    color: var(--color-text-muted);
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 500;
  }

  .prompt-section {
    margin-bottom: var(--spacing-xl);
  }

  .parameters {
    margin-bottom: var(--spacing-xl);
  }

  .parameters-details {
    background: var(--color-background-secondary);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: var(--spacing-lg);
  }

  .parameters-summary {
    cursor: pointer;
    color: var(--color-text-muted);
    font-size: 0.875rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    list-style: none;
  }

  .parameters-summary::-webkit-details-marker {
    display: none;
  }

  .parameters-summary::before {
    content: '▶';
    display: inline-block;
    margin-right: var(--spacing-sm);
    transition: transform 0.2s;
  }

  details[open] .parameters-summary::before {
    transform: rotate(90deg);
  }

  .parameters-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--spacing-xl);
    margin-top: var(--spacing-lg);
  }

  .parameter label {
    display: block;
    margin-bottom: var(--spacing-sm);
    color: var(--color-text);
    font-size: 0.875rem;
    font-weight: 500;
  }

  .parameter input[type="range"] {
    width: 100%;
  }

  .parameter input[type="number"] {
    width: 100%;
    padding: var(--spacing-sm);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    background: var(--color-background);
    color: var(--color-text);
  }

  .parameter.full-width {
    grid-column: 1 / -1;
  }

  .parameter input[type="checkbox"] {
    margin-right: var(--spacing-sm);
    transform: scale(1.2);
    cursor: pointer;
  }

  .prompt-images-section {
    margin-top: var(--spacing-xl);
    padding-top: var(--spacing-xl);
    border-top: 1px solid var(--color-border);
  }

  .section-title {
    margin: 0 0 var(--spacing-sm);
    color: var(--color-text);
    font-size: 1rem;
    font-weight: 500;
  }

  .section-description {
    margin: 0 0 var(--spacing-lg);
    color: var(--color-text-muted);
    font-size: 0.875rem;
  }

  .actions {
    display: flex;
    justify-content: center;
  }

  .btn-primary {
    background: var(--color-accent);
    color: white;
    border: none;
    padding: var(--spacing-md) var(--spacing-2xl);
    border-radius: var(--radius-md);
    font-size: 1rem;
    font-weight: 500;
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-sm);
    transition: all 0.2s;
  }

  .btn-primary:hover:not(:disabled) {
    background: var(--color-accent-dark);
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
  }

  .btn-primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-secondary {
    background: var(--color-background);
    color: var(--color-accent);
    border: 1px solid var(--color-accent);
    padding: var(--spacing-md) var(--spacing-2xl);
    border-radius: var(--radius-md);
    font-size: 1rem;
    font-weight: 500;
    margin-top: var(--spacing-xl);
    transition: all 0.2s;
  }

  .btn-secondary:hover {
    background: var(--color-accent);
    color: white;
  }

  .results {
    text-align: center;
  }

  .results-actions {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--spacing-md);
    margin-top: var(--spacing-xl);
  }

  .hint {
    font-size: 0.875rem;
    color: var(--color-text-muted);
    font-style: italic;
  }

  @media (max-width: 768px) {
    .upload-grid {
      grid-template-columns: 1fr;
    }

    .divider {
      transform: rotate(90deg);
      height: 40px;
    }
  }
</style>