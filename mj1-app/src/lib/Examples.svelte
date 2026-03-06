<script>
  export let onSelectExample;

  const examples = [
    {
      id: 1,
      prompt: "Which one of these is a more artistically appealing album cover?",
      imageA: "/bad.jpeg",
      imageB: "/off_the_wall.jpeg",
      imageALabel: "Bad",
      imageBLabel: "Off The Wall"
    },
    {
      id: 2,
      prompt: "Which one of these two images has a more intergalactic theme?",
      imageA: "/space_jam1.jpg",
      imageB: "/spacejam2.jpg",
      imageALabel: "Space Jam 1",
      imageBLabel: "Space Jam 2"
    },
    {
      id: 3,
      prompt: "Which of these street art pieces evokes the strongest emotional response?",
      imageA: "/banksy.jpeg",
      imageB: "/blek.jpeg",
      imageALabel: "Banksy",
      imageBLabel: "Blek"
    },
    {
      id: 4,
      prompt: "Which one inspires you the most?",
      imageA: "/tony.jpeg",
      imageB: "/harvey.jpg",
      imageALabel: "Tony",
      imageBLabel: "Harvey"
    }
  ];

  async function loadExample(example) {
    if (example.disabled) return;

    try {
      const [responseA, responseB] = await Promise.all([
        fetch(example.imageA),
        fetch(example.imageB)
      ]);

      const [blobA, blobB] = await Promise.all([
        responseA.blob(),
        responseB.blob()
      ]);

      const imageDataA = await blobToDataURL(blobA);
      const imageDataB = await blobToDataURL(blobB);

      onSelectExample({
        imageA: imageDataA,
        imageB: imageDataB,
        prompt: example.prompt,
        autoRun: true
      });
    } catch (error) {
      console.error('Failed to load example:', error);
    }
  }

  function blobToDataURL(blob) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  }
</script>

<section class="examples-section">
  <h2 class="examples-title">Try These Examples</h2>
  <p class="examples-subtitle">Click on an example to load it instantly</p>

  <div class="examples-grid">
    {#each examples as example}
      <button
        class="example-card"
        class:disabled={example.disabled}
        on:click={() => loadExample(example)}
        disabled={example.disabled}
      >
        {#if !example.disabled}
          <div class="example-images">
            <img src={example.imageA} alt={example.imageALabel} class="example-thumb" />
            <span class="vs-label">vs</span>
            <img src={example.imageB} alt={example.imageBLabel} class="example-thumb" />
          </div>
        {:else}
          <div class="example-placeholder">
            <svg width="60" height="60" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" opacity="0.3"/>
              <path d="M3 15L8 10L13 15" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" opacity="0.3"/>
              <path d="M14 13L17 10L21 14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" opacity="0.3"/>
              <circle cx="9" cy="8" r="2" stroke="currentColor" stroke-width="1.5" opacity="0.3"/>
            </svg>
          </div>
        {/if}
        <p class="example-prompt">{example.prompt}</p>
      </button>
    {/each}
  </div>
</section>

<style>
  .examples-section {
    margin-top: var(--spacing-2xl);
    padding: var(--spacing-2xl) 0;
    border-top: 1px solid var(--color-border);
  }

  .examples-title {
    text-align: center;
    font-size: 1.75rem;
    font-weight: 300;
    margin-bottom: var(--spacing-sm);
    color: var(--color-text);
  }

  .examples-subtitle {
    text-align: center;
    color: var(--color-text-muted);
    margin-bottom: var(--spacing-2xl);
    font-size: 0.95rem;
  }

  .examples-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-xl);
    max-width: 900px;
    margin: 0 auto;
  }

  .example-card {
    background: var(--color-background-secondary);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: var(--spacing-lg);
    cursor: pointer;
    transition: all 0.2s;
    text-align: center;
  }

  .example-card:hover:not(.disabled) {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
    border-color: var(--color-accent);
  }

  .example-card.disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .example-images {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-lg);
    padding: var(--spacing-md);
    background: var(--color-background);
    border-radius: var(--radius-md);
  }

  .example-thumb {
    width: 80px;
    height: 80px;
    object-fit: cover;
    border-radius: var(--radius-sm);
    border: 1px solid var(--color-border);
  }

  .vs-label {
    color: var(--color-text-muted);
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 500;
  }

  .example-placeholder {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 120px;
    margin-bottom: var(--spacing-lg);
    background: var(--color-background);
    border-radius: var(--radius-md);
    color: var(--color-text-muted);
  }

  .example-prompt {
    font-size: 1.125rem;
    color: var(--color-text);
    line-height: 1.5;
    font-weight: 400;
  }

  @media (max-width: 768px) {
    .examples-grid {
      grid-template-columns: 1fr;
    }
  }
</style>