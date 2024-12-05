<template>
  <div class="background">
    <div class="grid">
      <!-- Left Column -->
      <div class="icon">
        <Icon
          name="i-material-symbols:lab-research-outline"
          size="120"
          color="var(--color-cold-night)"
        />
      </div>

      <!-- Right Column -->
      <div class="text">
        <h2>The Choice of Law Dataverse is Open Research</h2>
        <p>
          The Dataverse promotes sharing, preserving, citing, exploring and
          analyzing research data on choice of law
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* General Layout */
.background {
  background-color: var(--color-cold-cream); /* Use the CSS variable */
  padding: 36px 48px 60px 48px;
}

/* Grid Layout for Two Columns */
.grid {
  display: grid;
  grid-template-columns: 1fr 2fr; /* Adjust column sizes as needed */
  column-gap: 24px; /* Space between columns */
  align-items: center; /* Vertically center the content */
}

.icon {
  display: flex;
  justify-content: center; /* Horizontally center the icon */
  align-items: center; /* Vertically center the icon */
  padding-right: 24px;
}

/* Text Styling */
.text h2 {
  margin-top: 0px !important;
  margin-bottom: 16px; /* Adjust spacing */
}

.text p {
  margin: 0;
}
</style>
