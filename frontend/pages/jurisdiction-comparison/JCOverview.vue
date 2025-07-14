<template>
  <div>
    <div class="jc-grid jc-overview-row">
      <div class="jc-col-1">
        <h2>Overview</h2>
      </div>
      <div class="jc-col-2 jc-empty"></div>
      <div class="jc-col-3 jc-empty"></div>
      <div class="jc-col-4 jc-empty"></div>
    </div>
    <hr class="jc-hr" />
    <div class="jc-grid jc-data-row">
      <div class="jc-col-1 jc-empty"></div>
      <div class="jc-col-2">
        <div class="result-value-medium">
          <span>Civil Law</span><br />
          <span>44 court decisions</span><br />
          <span>1 domestic instrument</span><br />
          <span>0 arbitration laws</span>
        </div>
      </div>
      <div class="jc-col-3">
        <div class="result-value-medium">
          <span>Civil Law</span><br />
          <span>44 court decisions</span><br />
          <span>1 domestic instrument</span><br />
          <span>0 arbitration laws</span>
        </div>
      </div>
      <div class="jc-col-4">
        <div class="result-value-medium">
          <span>Civil Law</span><br />
          <span>44 court decisions</span><br />
          <span>1 domestic instrument</span><br />
          <span>0 arbitration laws</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.jc-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  align-items: start;
  gap: 0 1.5rem;
}

.jc-overview-row {
  margin-bottom: 0;
}

.jc-data-row {
  margin-top: 0;
}

.jc-col-1 {
  grid-column: 1;
}
.jc-col-2 {
  grid-column: 2;
}
.jc-col-3 {
  grid-column: 3;
}
.jc-col-4 {
  grid-column: 4;
}

.jc-empty {
  /* Empty cell for layout spacing */
}

.jc-hr {
  margin: 16px 0 24px 0;
  border: none;
  border-top: 1px solid var(--color-cold-night, #222);
}

.result-value-medium {
  font-weight: 400 !important;
}
</style>
