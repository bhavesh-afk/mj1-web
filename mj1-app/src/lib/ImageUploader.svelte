<script>
  export let label = 'Upload Image';
  export let image = null;

  let isDragging = false;
  let inputElement;

  function handleDrop(e) {
    e.preventDefault();
    isDragging = false;

    const file = e.dataTransfer?.files[0] || e.target.files?.[0];
    if (file) {
      // Only allow JPG/JPEG and PNG
      const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
      if (!validTypes.includes(file.type.toLowerCase())) {
        alert('Only JPG/JPEG and PNG images are supported. GIF, SVG, and other formats may cause reasoning errors.');
        return;
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        image = e.target.result;
      };
      reader.readAsDataURL(file);
    }
  }

  function handleDragOver(e) {
    e.preventDefault();
    isDragging = true;
  }

  function handleDragLeave(e) {
    e.preventDefault();
    isDragging = false;
  }

  function handleClick() {
    inputElement.click();
  }

  function removeImage() {
    image = null;
  }
</script>

<div
  class="upload-container {isDragging ? 'dragging' : ''} {image ? 'has-image' : ''}"
  on:drop={handleDrop}
  on:dragover={handleDragOver}
  on:dragleave={handleDragLeave}
  role="button"
  tabindex="0"
>
  <div class="label">{label}</div>

  {#if image}
    <div class="image-preview">
      <img src={image} alt={label} />
      <button class="remove-btn" on:click|stopPropagation={removeImage}>
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path d="M12 4L4 12M4 4l8 8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </button>
    </div>
  {:else}
    <button class="upload-area" on:click={handleClick} type="button">
      <svg width="48" height="48" viewBox="0 0 48 48" fill="none" class="upload-icon">
        <rect x="4" y="8" width="40" height="32" rx="4" stroke="currentColor" stroke-width="2"/>
        <circle cx="34" cy="18" r="4" stroke="currentColor" stroke-width="2"/>
        <path d="M4 32L16 20L24 28L32 20L44 32" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <p class="upload-text">Drop image here or click to browse</p>
      <p class="upload-hint">Supports JPG and PNG only</p>
    </button>
  {/if}

  <input
    type="file"
    accept="image/jpeg,image/jpg,image/png"
    on:change={handleDrop}
    bind:this={inputElement}
    style="display: none"
  />
</div>

<style>
  .upload-container {
    background: var(--color-background-secondary);
    border: 2px dashed var(--color-border);
    border-radius: var(--radius-lg);
    padding: var(--spacing-xl);
    transition: all 0.2s;
    position: relative;
    min-height: 300px;
    display: flex;
    flex-direction: column;
  }

  .upload-container:hover {
    border-color: var(--color-accent);
    background: var(--color-background);
  }

  .upload-container.dragging {
    border-color: var(--color-accent);
    background: var(--color-background);
    border-style: solid;
  }

  .upload-container.has-image {
    border-style: solid;
    border-color: var(--color-accent);
  }

  .label {
    position: absolute;
    top: -12px;
    left: 20px;
    background: var(--color-background);
    padding: 0 var(--spacing-sm);
    color: var(--color-text);
    font-size: 0.875rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .upload-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    background: transparent;
    border: none;
    width: 100%;
    padding: var(--spacing-xl);
  }

  .upload-icon {
    color: var(--color-text-muted);
    margin-bottom: var(--spacing-lg);
  }

  .upload-text {
    color: var(--color-text);
    font-size: 1rem;
    margin: 0 0 var(--spacing-sm);
  }

  .upload-hint {
    color: var(--color-text-muted);
    font-size: 0.875rem;
    margin: 0;
  }

  .image-preview {
    position: relative;
    height: 100%;
    min-height: 250px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .image-preview img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    border-radius: var(--radius-md);
  }

  .remove-btn {
    position: absolute;
    top: var(--spacing-md);
    right: var(--spacing-md);
    width: 32px;
    height: 32px;
    border-radius: var(--radius-sm);
    background: var(--color-background);
    color: var(--color-text);
    border: 1px solid var(--color-border);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s;
  }

  .remove-btn:hover {
    background: var(--color-error);
    color: white;
    border-color: var(--color-error);
  }
</style>