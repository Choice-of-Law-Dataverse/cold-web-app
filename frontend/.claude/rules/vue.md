---
paths: ["*.vue"]
---

- Always `<script setup lang="ts">`, never Options API
- Only Vue/Nuxt built-ins (ref, computed, useRoute, etc.) are auto-imported
- Custom composables, utils, and third-party libraries require explicit imports
