<template>
  <div class="relative">
    <!-- Animated glow background -->
    <div class="glow-pulse absolute inset-0" />

    <svg
      width="140"
      height="140"
      viewBox="0 0 140 140"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      class="relative"
    >
      <!-- Document stack (back) -->
      <rect
        x="35"
        y="25"
        width="55"
        height="70"
        rx="6"
        class="fill-cold-purple/10 dark:fill-cold-purple/20"
      />
      <rect
        x="30"
        y="20"
        width="55"
        height="70"
        rx="6"
        class="fill-cold-purple/20 dark:fill-cold-purple/30"
      />

      <!-- Main document -->
      <rect
        x="25"
        y="15"
        width="55"
        height="70"
        rx="6"
        fill="white"
        class="dark:fill-gray-800"
        filter="url(#shadow)"
      />
      <rect
        x="25"
        y="15"
        width="55"
        height="70"
        rx="6"
        fill="none"
        class="stroke-cold-purple/30"
        stroke-width="1.5"
      />

      <!-- Document lines -->
      <rect
        x="33"
        y="28"
        width="30"
        height="3"
        rx="1.5"
        class="fill-cold-purple/40"
      />
      <rect
        x="33"
        y="36"
        width="39"
        height="2"
        rx="1"
        class="fill-gray-200 dark:fill-gray-600"
      />
      <rect
        x="33"
        y="42"
        width="35"
        height="2"
        rx="1"
        class="fill-gray-200 dark:fill-gray-600"
      />
      <rect
        x="33"
        y="48"
        width="39"
        height="2"
        rx="1"
        class="fill-gray-200 dark:fill-gray-600"
      />
      <rect
        x="33"
        y="54"
        width="28"
        height="2"
        rx="1"
        class="fill-gray-200 dark:fill-gray-600"
      />
      <rect
        x="33"
        y="62"
        width="20"
        height="3"
        rx="1.5"
        class="fill-cold-teal/40"
      />
      <rect
        x="33"
        y="70"
        width="35"
        height="2"
        rx="1"
        class="fill-gray-200 dark:fill-gray-600"
      />

      <!-- AI Circle with sparkle -->
      <circle cx="95" cy="45" r="28" fill="url(#aiGradient)" />
      <circle
        cx="95"
        cy="45"
        r="28"
        fill="none"
        stroke="white"
        stroke-width="2"
        opacity="0.3"
      />

      <!-- AI Sparkle icon -->
      <path
        d="M95 30 L97.5 40 L107 43 L97.5 46 L95 56 L92.5 46 L83 43 L92.5 40 Z"
        fill="white"
      />
      <circle cx="103" cy="35" r="2" fill="white" opacity="0.6" />
      <circle cx="87" cy="53" r="1.5" fill="white" opacity="0.6" />

      <!-- Magnifying glass -->
      <circle
        cx="75"
        cy="95"
        r="18"
        fill="white"
        class="dark:fill-gray-800"
        filter="url(#shadow)"
      />
      <circle
        cx="75"
        cy="95"
        r="18"
        fill="none"
        class="stroke-cold-teal"
        stroke-width="3"
      />
      <circle
        cx="75"
        cy="95"
        r="12"
        fill="none"
        class="stroke-cold-teal/30"
        stroke-width="2"
      />
      <line
        x1="88"
        y1="108"
        x2="102"
        y2="122"
        class="stroke-cold-teal"
        stroke-width="4"
        stroke-linecap="round"
      />

      <!-- Checkmark in magnifier -->
      <path
        d="M68 95 L73 100 L83 90"
        fill="none"
        class="stroke-cold-teal"
        stroke-width="2.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      />

      <!-- Gradient definitions -->
      <defs>
        <linearGradient
          id="aiGradient"
          x1="67"
          y1="17"
          x2="123"
          y2="73"
          gradientUnits="userSpaceOnUse"
        >
          <stop stop-color="#6F4DFA" />
          <stop offset="1" stop-color="#0891B2" />
        </linearGradient>
        <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="4" stdDeviation="6" flood-opacity="0.1" />
        </filter>
      </defs>
    </svg>
  </div>
</template>
