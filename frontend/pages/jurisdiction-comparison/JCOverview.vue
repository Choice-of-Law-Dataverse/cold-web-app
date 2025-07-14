<template>
  <div class="jc-grid">
    <div class="jc-col jc-col-1">
      <h2>Overview</h2>
    </div>
    <div class="jc-col jc-col-2">
      <div class="result-value-medium">
        <span>Col 2 - Civil Law</span><br />
        <span>44 court decisions</span><br />
        <span>1 domestic instrument</span><br />
        <span>0 arbitration laws</span>
      </div>
    </div>
    <div class="jc-col jc-col-3">
      <div class="result-value-medium">
        <span>Col 3 - Civil Law</span><br />
        <span>44 court decisions</span><br />
        <span>1 domestic instrument</span><br />
        <span>0 arbitration laws</span>
      </div>
    </div>
    <div class="jc-col jc-col-4">
      <div class="result-value-medium">
        <span>Col 4 - Civil Law</span><br />
        <span>44 court decisions</span><br />
        <span>1 domestic instrument</span><br />
        <span>0 arbitration laws</span>
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

.jc-col {
  /* Optional: for debugging columns */
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

.result-value-medium {
  font-weight: 400 !important;
}
</style>
