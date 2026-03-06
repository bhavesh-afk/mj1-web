<script>
  export let label = 'Upload Images';
  export let images = [];
  export let maxImages = 5;

  let isDragging = false;
  let inputElement;

  function handleFiles(files) {
    for (let file of files) {
      if (file && images.length < maxImages) {
        // Only allow JPG/JPEG and PNG
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
        if (!validTypes.includes(file.type.toLowerCase())) {
          alert('Only JPG/JPEG and PNG images are supported. GIF, SVG, and other formats may cause reasoning errors.');
          continue;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
          images = [...images, e.target.result];
        };
        reader.readAsDataURL(file);
      }
    }
  }

  function handleDrop(e) {
    e.preventDefault();
    isDragging = false;
    const files = e.dataTransfer?.files || e.target.files;
    if (files) {
      handleFiles(files);
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

  function removeImage(index) {
    images = images.filter((_, i) => i !== index);
  }
</script>

<div
  class="multi-upload-container {isDragging ? 'dragging' : ''}"
  on:drop={handleDrop}
  on:dragover={handleDragOver}
  on:dragleave={handleDragLeave}
  role="button"
  tabindex="0"
>
  <div class="label">{label} ({images.length}/{maxImages})</div>

  <div class="images-grid">
    {#each images as image, index}
      <div class="image-thumbnail">
        <img src={image} alt="{label} {index + 1}" />
        <button class="remove-btn" on:click|stopPropagation={() => removeImage(index)}>
          <svg width="12" height="12" viewBox="0 0 16 16" fill="none">
            <path d="M12 4L4 12M4 4l8 8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>
      </div>
    {/each}

    {#if images.length < maxImages}
      <button class="add-image-btn" on:click={handleClick} type="button">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
          <path d="M12 5v14m-7-7h14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <span>Add Image</span>
      </button>
    {/if}
  </div>

  {#if images.length === 0}
    <button class="upload-area" on:click={handleClick} type="button">
      <svg width="48" height="48" viewBox="0 0 48 48" fill="none" class="upload-icon">
        <rect x="4" y="8" width="40" height="32" rx="4" stroke="currentColor" stroke-width="2"/>
        <circle cx="34" cy="18" r="4" stroke="currentColor" stroke-width="2"/>
        <path d="M4 32L16 20L24 28L32 20L44 32" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <p class="upload-text">Drop images here or click to browse</p>
      <p class="upload-hint">Upload up to {maxImages} images (JPG/PNG only)</p>
    </button>
  {/if}

  <input
    type="file"
    accept="image/jpeg,image/jpg,image/png"
    multiple
    on:change={handleDrop}
    bind:this={inputElement}
    style="display: none"
  />
</div>

<style>
  .multi-upload-container {
    background: var(--color-background-secondary);
    border: 2px dashed var(--color-border);
    border-radius: var(--radius-lg);
    padding: var(--spacing-xl);
    transition: all 0.2s;
    position: relative;
    min-height: 200px;
  }

  .multi-upload-container:hover {
    border-color: var(--color-accent);
    background: var(--color-background);
  }

  .multi-upload-container.dragging {
    border-color: var(--color-accent);
    background: var(--color-background);
    border-style: solid;
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

  .images-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: var(--spacing-md);
  }

  .image-thumbnail {
    position: relative;
    aspect-ratio: 1;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    overflow: hidden;
    background: var(--color-background);
  }

  .image-thumbnail img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .remove-btn {
    position: absolute;
    top: 4px;
    right: 4px;
    width: 24px;
    height: 24px;
    border-radius: var(--radius-sm);
    background: rgba(255, 255, 255, 0.9);
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

  .add-image-btn {
    aspect-ratio: 1;
    border: 2px dashed var(--color-border);
    border-radius: var(--radius-md);
    background: transparent;
    color: var(--color-text-muted);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-sm);
    cursor: pointer;
    transition: all 0.2s;
  }

  .add-image-btn:hover {
    border-color: var(--color-accent);
    color: var(--color-accent);
    background: var(--color-background);
  }

  .add-image-btn span {
    font-size: 0.75rem;
    font-weight: 500;
  }

  .upload-area {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    background: transparent;
    border: none;
    width: 100%;
    padding: var(--spacing-xl);
    min-height: 150px;
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
</style>