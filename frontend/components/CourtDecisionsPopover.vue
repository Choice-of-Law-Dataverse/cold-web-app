<template>
    <UPopover overlay>
      <UButton color="white" label="Open" />
  
      <!-- Accessing the `close` method in the panel slot -->
      <template #panel="{ close }">
      <div class="p-4 custom-popover-width" style="position: relative;">
        <!-- Close link with icon -->
        <a href="#" class="close-link" @click.prevent="close">
          <!-- Icon before the text -->
          <span class="icon-wrapper">
            <UIcon name="i-material-symbols:close" />
        </span>
          Close
        </a>
          
          <p class="result-key">CASE TITLE</p>
          <p class="result-value">Federal Court, 03.07.1985 - BGE 111 II 175 </p>
          
        <span class="icon-wrapper">
            <UIcon name="i-material-symbols:file-open" />
        </span>

        <a class="result-value">View original PDF</a>
          
          <p><br></p>
  
          <p class="result-key">JURISDICTION</p>
          <p class="result-value">Switzerland</p>
  
          <p class="result-key">ABSTRACT</p>
          <p class="result-value">…</p>
  
          <p class="result-key">RELEVANT FACTS / SUMMARY OF THE CASE</p>
          <p class="result-value">…</p>

          <p class="result-key">RELEVANT RULES OF LAW INVOLVED</p>
          <p class="result-value">…</p>

          <p class="result-key">CHOICE OF LAW ISSUE</p>
          <p class="result-value">…</p>

          <p class="result-key">COURT'S POSITION</p>
          <p class="result-value">…</p>

          <p class="result-key">TEXT OF THE RELEVANT LEGAL PROVISIONS</p>
          <p class="result-value">…</p>

          <p class="result-key">QUOTE</p>
          <p class="result-value">…</p>

          <p class="result-key">TRANSLATED EXCERPT</p>
          <p class="result-value">…</p>
        </div>
      </template>
    </UPopover>
  </template>
  

<style scoped>
  /* Container style is defined inline in the template */

  .custom-popover-width {
  width: 60vw;
  position: relative;
  margin: 3em;
}

.close-link {
  position: absolute;
  top: -20px;
  right: -10px;
  text-decoration: none;
  cursor: pointer;
  display: flex; /* Use flexbox to align icon and text horizontally */
  align-items: center; /* Align icon and text vertically */
}

.icon-wrapper {
    margin-right: 4px;
    margin-top: 5px;
}
  
  .result-item {
    margin-bottom: 1rem;
  }
  
  .result-key {
    font-size: x-small;
    font-weight: bold;
  }
  
  /* Adding styles to ensure text wrapping */
  .result-value {
    word-wrap: break-word; /* Allows breaking within words if necessary */
    word-break: break-word; /* Breaks words that are too long */
    white-space: pre-wrap; /* Preserves whitespace and line breaks, but also allows wrapping */
    margin-bottom: 2em;
  }

  a {
    text-decoration: underline;
    text-underline-offset: 6px;
    text-decoration-thickness: 1px;
  }
  </style>
  