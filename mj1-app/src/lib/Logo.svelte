<script>
  export let size = 80; // Default size

  const sizeMap = {
    60: '-80',
    80: '-80',
    120: '-120',
    180: '-180'
  };

  const suffix = sizeMap[size] || '-80';
</script>

<div class="logo-container">
  <picture>
    <source
      srcset="/images/mj1-fedora{suffix}.avif"
      type="image/avif"
    />
    <source
      srcset="/images/mj1-fedora{suffix}.webp"
      type="image/webp"
    />
    <img
      src="/images/mj1-fedora{suffix}.png"
      alt="MJ1 - Multimodal Judge"
      class="logo"
      width={size}
      height={size}
      loading="eager"
      decoding="async"
    />
  </picture>
</div>

<style>
  .logo-container {
    display: inline-block;
    position: relative;
  }

  .logo {
    width: 80px;
    height: 80px;
    object-fit: contain;
    filter: contrast(1.1);
    /* Using mix-blend-mode to remove light background */
    mix-blend-mode: multiply;
    background: white;
    border-radius: 8px;
  }

  @media (max-width: 768px) {
    .logo {
      width: 60px;
      height: 60px;
    }
  }
</style>