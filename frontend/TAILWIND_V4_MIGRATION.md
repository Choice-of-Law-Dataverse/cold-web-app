# Tailwind CSS v4 Migration Guide

This document outlines the steps needed to migrate from Tailwind CSS v3 to v4 when the ecosystem is ready.

## Current Status (January 2025)

- ✅ Upgraded from Tailwind v3.4.14 to v3.4.17 (latest v3)
- ❌ Cannot fully migrate to v4 due to ecosystem compatibility issues

## Blocking Dependencies

1. **@nuxt/ui** - Not compatible with Tailwind v4
   - Issue: Module expects `theme.colors` in the old format
   - Impact: Build fails when trying to access Tailwind configuration

2. **@nuxtjs/tailwindcss** - Limited v4 support
   - Beta version (7.0.0-beta.1) still has compatibility issues
   - Stable version (6.14.0) doesn't support v4

## Migration Steps (For Future Reference)

### 1. Update Dependencies
```bash
npm install tailwindcss@latest @tailwindcss/postcss
npm uninstall @tailwindcss/forms @tailwindcss/aspect-ratio  # Built-in to v4
```

### 2. Update CSS Imports
Replace in `assets/styles.scss`:
```scss
// Old (v3)
@tailwind base;
@tailwind components;
@tailwind utilities;

// New (v4)
@import "tailwindcss";
```

### 3. Update Configuration
Option A: Keep JS config (hybrid approach)
- Remove old plugins that are now built-in
- Update any breaking changes in config API

Option B: Migrate to CSS-only config
```scss
@import "tailwindcss";

@theme {
  --color-cold-purple: #6F4DFA;
  /* ... other custom colors */
}
```

### 4. Update PostCSS Configuration
Create `postcss.config.js`:
```js
export default {
  plugins: {
    '@tailwindcss/postcss': {},
    autoprefixer: {},
  },
}
```

### 5. Update Nuxt Configuration
- Remove old CSS imports
- Update tailwindcss module configuration

## Features Available in v4

- Built-in form styles (previously @tailwindcss/forms)
- Built-in aspect ratio utilities (previously @tailwindcss/aspect-ratio)
- Improved performance and build times
- New CSS-first configuration approach
- Better CSS custom properties support

## Recommended Timeline

Wait for these conditions before migrating:

1. **@nuxt/ui** releases v4-compatible version
2. **@nuxtjs/tailwindcss** stable v4 support
3. All other Nuxt modules in the project support v4

## Testing Strategy

When ready to migrate:

1. Create a feature branch
2. Follow migration steps
3. Test all UI components thoroughly
4. Verify custom color CSS variables still work
5. Check form styling (now built-in)
6. Test responsive design and aspect ratios
7. Validate production build