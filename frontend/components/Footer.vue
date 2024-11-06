<template>
  <footer class="footer">
    <div class="footer-content">
      <p>© 2024 Your Company Name. All rights reserved.</p>
      <nav class="footer-links">
        <NuxtLink to="/about">About</NuxtLink>
        <NuxtLink to="/contact">Contact</NuxtLink>
        <NuxtLink to="/privacy">Privacy Policy</NuxtLink>
      </nav>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  width: 100%;
  background-color: var(--color-cold-night); /* Apply background color */
  color: white; /* Text color */
  padding: 20px 0; /* Spacing inside the footer */
}

.footer-content {
  max-width: var(--container-width); /* Center content within the grid */
  margin: 0 auto;
  padding: 0 var(--gutter-width); /* Add padding on sides for alignment */
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-links {
  display: flex;
  gap: 24px; /* Space between links */
}

.footer-links a {
  color: white; /* Link color */
  text-decoration: none;
}

.footer-links a:hover {
  text-decoration: underline; /* Underline on hover */
}
</style>
