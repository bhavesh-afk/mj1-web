<script>
  export let judgment;
  export let imageA;
  export let imageB;

  function extractAnalysis(fullResponse) {
    if (!fullResponse) return judgment.explanation;

    const match = fullResponse.match(/<evaluate_criteria>([\s\S]*?)<\/evaluate_criteria>/);
    if (match && match[1]) {
      return match[1].trim();
    }
    return judgment.explanation;
  }

  function formatAnalysisHTML(text) {
    if (!text) return '';

    const paragraphs = text.split(/\n\n+/);

    return paragraphs.map(para => {
      const numberedMatch = para.match(/^(\d+)\.\s+\*\*(.*?)\*\*:?\s*(.*)/s);
      if (numberedMatch) {
        const [, num, title, content] = numberedMatch;
        const cleanContent = content.trim().replace(/\n/g, ' ');
        const isNotApplicable = cleanContent.includes('Not Applicable') || cleanContent.includes('not applicable');

        return `
          <div class="analysis-item">
            <div class="analysis-number">${num}</div>
            <div class="analysis-content">
              <strong class="analysis-title">${title.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</strong>
              <p class="${isNotApplicable ? 'not-applicable' : ''}">${cleanContent}</p>
            </div>
          </div>
        `;
      }

      let formatted = para
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');

      return `<p class="analysis-paragraph">${formatted}</p>`;
    }).join('');
  }

  $: analysisText = extractAnalysis(judgment.fullResponse);
  $: formattedAnalysis = formatAnalysisHTML(analysisText);
</script>

<div class="result-container">
  <div class="winner-section">
    <h2 class="result-title">Judgment Result</h2>
    <div class="winner-badge">
      <span class="winner-label">Winner</span>
      <span class="winner-value">Image {judgment.winner}</span>
    </div>
  </div>

  <div class="scores-section">
    <div class="score-card {judgment.winner === 'A' ? 'winner' : ''}">
      <h3 class="score-label">Image A</h3>
      <div class="score-value">{judgment.scoreA}/10</div>
    </div>

    <div class="divider">
      <span>vs</span>
    </div>

    <div class="score-card {judgment.winner === 'B' ? 'winner' : ''}">
      <h3 class="score-label">Image B</h3>
      <div class="score-value">{judgment.scoreB}/10</div>
    </div>
  </div>

  <div class="images-section">
    <div class="image-card {judgment.winner === 'A' ? 'winner' : ''}">
      <img src={imageA} alt="Image A" />
      <div class="image-label">Image A</div>
    </div>
    <div class="image-card {judgment.winner === 'B' ? 'winner' : ''}">
      <img src={imageB} alt="Image B" />
      <div class="image-label">Image B</div>
    </div>
  </div>

  <div class="explanation-section">
    <h3 class="explanation-title">Analysis</h3>
    <div class="explanation-content">
      {#if analysisText}
        <pre class="analysis-formatted">{analysisText}</pre>
      {:else}
        <p class="analysis-paragraph">{judgment.explanation}</p>
      {/if}
    </div>
  </div>

  {#if judgment.fullResponse}
    <details class="full-response">
      <summary class="response-summary">Full Response with XML Tags</summary>
      <pre class="response-content">{judgment.fullResponse}</pre>
    </details>
  {/if}
</div>

<style>
  .result-container {
    max-width: 1000px;
    margin: 0 auto;
  }

  .winner-section {
    text-align: center;
    margin-bottom: var(--spacing-2xl);
  }

  .result-title {
    font-size: 2rem;
    font-weight: 300;
    color: var(--color-text);
    margin-bottom: var(--spacing-lg);
  }

  .winner-badge {
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-md);
    padding: var(--spacing-md) var(--spacing-xl);
    background: var(--color-accent);
    color: white;
    border-radius: var(--radius-lg);
  }

  .winner-label {
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    opacity: 0.9;
  }

  .winner-value {
    font-size: 1.25rem;
    font-weight: 600;
  }

  .scores-section {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    gap: var(--spacing-xl);
    margin-bottom: var(--spacing-2xl);
    align-items: center;
  }

  .score-card {
    background: var(--color-background-secondary);
    border: 2px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: var(--spacing-xl);
    text-align: center;
    transition: all 0.3s;
  }

  .score-card.winner {
    border-color: var(--color-accent);
    background: var(--color-background);
    transform: scale(1.05);
  }

  .score-label {
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--color-text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: var(--spacing-sm);
  }

  .score-card.winner .score-label {
    color: var(--color-accent);
  }

  .score-value {
    font-size: 2.5rem;
    font-weight: 300;
    color: var(--color-text);
  }

  .score-card.winner .score-value {
    color: var(--color-accent);
  }

  .divider {
    text-align: center;
    color: var(--color-text-muted);
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  .images-section {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--spacing-xl);
    margin-bottom: var(--spacing-2xl);
  }

  .image-card {
    position: relative;
    border: 2px solid var(--color-border);
    border-radius: var(--radius-lg);
    overflow: hidden;
    transition: all 0.3s;
  }

  .image-card.winner {
    border-color: var(--color-accent);
    box-shadow: 0 0 0 4px rgba(45, 127, 130, 0.1);
  }

  .image-card img {
    width: 100%;
    max-height: 400px;
    object-fit: contain;
    display: block;
    background: #f9f9f9;
  }

  .image-label {
    position: absolute;
    top: var(--spacing-md);
    left: var(--spacing-md);
    background: var(--color-background);
    color: var(--color-text);
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--radius-sm);
    font-size: 0.875rem;
    font-weight: 500;
    border: 1px solid var(--color-border);
  }

  .image-card.winner .image-label {
    background: var(--color-accent);
    color: white;
    border-color: var(--color-accent);
  }

  .explanation-section {
    background: var(--color-background-secondary);
    border-radius: var(--radius-lg);
    padding: var(--spacing-xl);
    margin-bottom: var(--spacing-xl);
  }

  .explanation-title {
    font-size: 1.125rem;
    font-weight: 500;
    color: var(--color-text);
    margin-bottom: var(--spacing-md);
    text-align: left;
  }

  .explanation-content {
    color: var(--color-text);
    line-height: 1.8;
    text-align: left;
  }

  .analysis-formatted {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 0.925rem;
    font-weight: 400;
    line-height: 1.7;
    white-space: pre-wrap;
    word-wrap: break-word;
    color: var(--color-text);
    background: var(--color-background);
    padding: var(--spacing-lg);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    margin: 0;
  }

  .analysis-item {
    display: flex;
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-lg);
    padding-bottom: var(--spacing-lg);
    border-bottom: 1px solid var(--color-border);
  }

  .analysis-item:last-child {
    margin-bottom: 0;
    padding-bottom: 0;
    border-bottom: none;
  }

  .analysis-number {
    flex-shrink: 0;
    width: 32px;
    height: 32px;
    background: var(--color-accent);
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 0.875rem;
  }

  .analysis-content {
    flex: 1;
  }

  .analysis-title {
    display: block;
    color: var(--color-text);
    font-weight: 600;
    font-size: 0.95rem;
    margin-bottom: var(--spacing-sm);
    text-transform: capitalize;
  }

  .analysis-content p {
    margin: 0;
    color: var(--color-text);
    font-size: 0.925rem;
    line-height: 1.7;
  }

  .analysis-content .not-applicable {
    color: var(--color-text-muted);
    font-style: italic;
  }

  .analysis-paragraph {
    margin: 0 0 var(--spacing-md);
    color: var(--color-text);
    line-height: 1.7;
  }

  .analysis-paragraph:last-child {
    margin-bottom: 0;
  }

  .analysis-paragraph strong {
    font-weight: 600;
    color: var(--color-text);
  }

  .full-response {
    background: var(--color-background-secondary);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: var(--spacing-lg);
  }

  .response-summary {
    cursor: pointer;
    color: var(--color-text-muted);
    font-size: 0.875rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    list-style: none;
  }

  .response-summary::-webkit-details-marker {
    display: none;
  }

  .response-content {
    margin-top: var(--spacing-lg);
    padding: var(--spacing-lg);
    background: var(--color-background);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 0.875rem;
    font-weight: 400;
    line-height: 1.6;
    color: var(--color-text);
    white-space: pre-wrap;
    word-break: break-word;
    text-align: left;
  }

  @media (max-width: 768px) {
    .scores-section,
    .images-section {
      grid-template-columns: 1fr;
    }

    .divider {
      transform: rotate(90deg);
      height: 40px;
    }

    .analysis-item {
      gap: var(--spacing-md);
    }

    .analysis-number {
      width: 28px;
      height: 28px;
      font-size: 0.75rem;
    }

    .analysis-title {
      font-size: 0.875rem;
    }

    .analysis-content p {
      font-size: 0.875rem;
    }
  }
</style>