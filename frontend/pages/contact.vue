<template>
  <div class="container">
    <div class="col-span-12">
      <UCard class="cold-ucard">
        <div class="main-content-grid">
          <div class="grid-item">
            <h2>Contact Us</h2>
            <p>
              We'd love to receive your questions, inquiries and feedback.<br />
              Just send us an email:
              <a href="mailto:mail@cold.global">mail@cold.global</a>
            </p>

            <h2>Stay Updated</h2>
            <p>
              Follow CoLD on
              <a
                href="https://www.linkedin.com/company/choice-of-law-dataverse"
                target="_blank"
                >LinkedIn</a
              >
              and subscribe to the newsletter on
              <a
                href="https://choiceoflawdataverse.substack.com/subscribe"
                target="_blank"
                >Substack</a
              >.
            </p>

            <h2>Visit Us</h2>
            <p>
              Our offices are in Lucerne, Switzerland: <br />
              <br />
              Universität Luzern<br />
              Inseliquai 8<br />
              Room INS-1<br />
              6005 Luzern<br />
              Switzerland
            </p>
          </div>
        </div>
      </UCard>
    </div>
  </div>
</template>

<style scoped>
.main-content-grid {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr)); /* 12-column layout */
  column-gap: var(--gutter-width); /* Gutter space between columns */
  padding: 32px; /* Optional padding to match the card's interior padding */
}

.grid-item {
  grid-column: 1 / span 6; /* Start in the 1st column, span across 6 columns */
  margin-bottom: 48px; /* Space between each key-value pair */
}

p {
  margin-bottom: 36px;
}

h2 {
  margin-bottom: 8px;
}
</style>
