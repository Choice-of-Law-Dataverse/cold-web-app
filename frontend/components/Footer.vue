<template>
  <footer class="footer">
    <div class="container">
      <div class="col-span-8 footer-text">
        <h2>Choice of Law<br />Dataverse</h2>
        <p style="margin-top: 12px">
          Funded by the<br />Swiss National Science Foundation
        </p>
      </div>
      <div class="col-span-4 footer-links">
        <NuxtLink to="/disclaimer">Disclaimer</NuxtLink>
        <NuxtLink to="/about">About</NuxtLink>
        <NuxtLink to="/contact">Contact</NuxtLink>
      </div>
    </div>
  </footer>
</template>

<style scoped>
h2 {
  font-size: 24px !important;
  line-height: 30px !important;
  font-weight: 700 !important;
  margin-left: -24px !important;
}

p {
  font-size: 16px !important;
  font-weight: 700 !important;
  line-height: 20px !important;
  margin-left: -24px !important;
}

.footer {
  width: 100%;
  background-color: var(--color-cold-night); /* Apply background color */
  color: white;
  padding: 60px 0 120px 0;
  margin-top: 240px;
}

.container {
  display: grid;
  grid-template-columns: repeat(12, var(--column-width));
  column-gap: var(--gutter-width);
  max-width: var(--container-width);
  margin: 0 auto;
  align-items: center;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(
    12,
    var(--column-width)
  ); /* Define 12 columns with custom width */
  column-gap: var(--gutter-width); /* Add gap between columns */
  max-width: var(--container-width); /* Align with main container width */
  margin: 0 auto;
  align-items: center;
}

.footer-text {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.footer-links {
  font-weight: 700 !important;
  text-align: right;
  margin-left: -24px !important;
  margin-top: -100px !important;
}

.footer-links a {
  color: white !important; /* Link color */
  text-decoration: none !important;
  margin-left: 36px;
}

.footer-links a:hover {
  text-decoration: none !important;
}
</style>
