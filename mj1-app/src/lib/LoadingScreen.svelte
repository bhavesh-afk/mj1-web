<script>
  export let isLoading = false;
</script>

{#if isLoading}
  <div class="loading-overlay">
    <div class="loading-content">
      <picture>
        <source
          srcset="/images/mj1-fedora-120.avif"
          type="image/avif"
        />
        <source
          srcset="/images/mj1-fedora-120.webp"
          type="image/webp"
        />
        <img
          src="/images/mj1-fedora-120.png"
          alt="MJ1 Loading"
          class="loading-logo"
          width="120"
          height="120"
          loading="eager"
        />
      </picture>
      <div class="loading-spinner"></div>
      <p class="loading-text">Processing judgment...</p>
    </div>
  </div>
{/if}

<style>
  .loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    animation: fadeIn 0.3s ease-out;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

  .loading-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2rem;
    padding: 3rem;
    background: rgba(255, 255, 255, 1);
    border-radius: 1.5rem;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
    animation: scaleIn 0.3s ease-out;
  }

  @keyframes scaleIn {
    from {
      transform: scale(0.9);
      opacity: 0;
    }
    to {
      transform: scale(1);
      opacity: 1;
    }
  }

  .loading-logo {
    width: 120px;
    height: 120px;
    object-fit: contain;
    filter: contrast(1.1);
    animation: pulse 2s ease-in-out infinite;
  }

  @keyframes pulse {
    0%, 100% {
      transform: scale(1);
    }
    50% {
      transform: scale(1.05);
    }
  }

  .loading-spinner {
    width: 48px;
    height: 48px;
    border: 3px solid rgba(45, 127, 130, 0.2);
    border-top-color: #2D7F82;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  .loading-text {
    margin: 0;
    color: #4CA9AC;
    font-size: 1.125rem;
    font-weight: 500;
    letter-spacing: 0.5px;
    animation: fadeInUp 0.5s ease-out;
  }

  @keyframes fadeInUp {
    from {
      transform: translateY(10px);
      opacity: 0;
    }
    to {
      transform: translateY(0);
      opacity: 1;
    }
  }

  /* Dark mode support - keeping white background */
  @media (prefers-color-scheme: dark) {
    /* Keep the white background even in dark mode */
    .loading-overlay {
      background: rgba(255, 255, 255, 0.85);
    }

    .loading-content {
      background: rgba(255, 255, 255, 1);
    }

    .loading-text {
      color: #4CA9AC;
    }

    .loading-spinner {
      border-color: rgba(76, 169, 172, 0.2);
      border-top-color: #4CA9AC;
    }
  }

  /* Mobile responsive */
  @media (max-width: 768px) {
    .loading-content {
      padding: 2rem;
    }

    .loading-logo {
      width: 80px;
      height: 80px;
    }

    .loading-spinner {
      width: 40px;
      height: 40px;
    }

    .loading-text {
      font-size: 1rem;
    }
  }
</style>