# Frontend - Agent Instructions

**Always reference these instructions first and only fallback to additional search and context gathering if the information in the instructions is incomplete or found to be in error.**

This is the frontend subproject of the CoLD (Choice of Law Dataverse) web application, built with Nuxt 3, Vue.js, TypeScript, and TailwindCSS.

## Code Standards

### TypeScript Requirements
- **Always use TypeScript**: Prefer `.ts` and `.vue` files over `.js`
- **Strong typing**: Define proper interfaces and types
- **No `any` types**: Use specific types or `unknown` with type guards

### File Organization
- **No barrel files**: Do not create `index.ts` files that re-export everything
- **Direct imports**: Import directly from specific files
- **Conventional commits**: Use semantic commit messages (feat:, fix:, docs:, style:, refactor:, test:, chore:)

## Setup and Development

### Initial Setup
```bash
cd frontend

# Install dependencies
npm install
# Takes: ~55 seconds. Font provider warnings are normal in restricted environments.
```

### Development Commands
```bash
# Development server
npm run dev
# Takes: ~30 seconds to start, runs on http://localhost:3000
# Ready when you see "Vite server built" and "Nuxt Nitro server built"
# Font provider warnings are NORMAL and safe to ignore

# Production build
npm run build  
# Takes: 3-4 minutes. NEVER CANCEL - set timeout to 300+ seconds minimum.
# Success indicated by "You can preview this build using node .output/server/index.mjs"

# Preview production build
npm run preview

# Generate static files
npm run generate
```

### Build Timing Guidelines

**CRITICAL: NEVER CANCEL BUILDS OR LONG-RUNNING COMMANDS**

| Command | Expected Time | Minimum Timeout | Notes |
|---------|---------------|-----------------|-------|
| `npm install` | 55 seconds | 180 seconds | Font provider warnings normal |
| `npm run build` | 3-4 minutes | 300 seconds | NEVER CANCEL - font warnings normal |
| `npm run dev` | 30 seconds | 120 seconds | Ready when Vite/Nitro servers built |

## Code Quality

### Linting and Formatting
```bash
# Format code with Prettier
npx prettier --write .
# Formats according to .prettierrc config (singleQuote: true, semi: false)

# Check formatting without fixing
npx prettier --check .

# ESLint (needs migration from v8 to v9 config format)
# Current .eslintrc.js needs to be migrated to eslint.config.js
```

### Validation Requirements
After making any code changes, ALWAYS perform these steps:

1. **Build Test**: `npm run build` - ensure it completes without errors
2. **Dev Server Test**: `npm run dev` - verify server starts successfully
3. **Basic Functionality**: Access http://localhost:3000 and verify HTML content loads
4. **Format Check**: `npx prettier --check .` - ensure code formatting

## Architecture

### Key Technologies
- **Nuxt 3**: Vue.js meta-framework with SSR
- **Vue.js 3**: Composition API preferred
- **TypeScript**: Strict typing enabled
- **TailwindCSS**: Utility-first CSS framework
- **Nuxt UI**: Component library

### Project Structure
```
frontend/
├── package.json          # Dependencies and scripts
├── nuxt.config.ts       # Nuxt configuration
├── .prettierrc          # Prettier formatting rules
├── .eslintrc.js         # ESLint config (needs v9 migration)
├── app.vue              # Root Vue component
├── pages/               # Route pages
├── components/          # Vue components  
├── composables/         # Vue composables
├── assets/              # CSS and static assets
└── public/              # Public static files
```

### Environment Variables
```bash
# Optional - for external integrations
NUXT_TURNSTILE_SITE_KEY=your-turnstile-site-key
NUXT_TURNSTILE_SECRET_KEY=your-turnstile-secret-key  
API_BASE_URL=https://your-api-endpoint
FASTAPI_API_TOKEN=your-api-token
NUXT_SITE_URL=https://your-site-url
NUXT_SITE_NAME="Your Site Name"
```

## Common Issues

### Font Provider Warnings
- **Issue**: Cannot connect to fonts.google.com, fonts.bunny.net, etc. in restricted environments
- **Impact**: Warning messages during build/dev, but functionality unaffected
- **Solution**: Warnings are normal and safe to ignore

### ESLint Configuration
- **Issue**: Current .eslintrc.js uses deprecated ESLint v8 format
- **Impact**: Direct ESLint execution may fail
- **Solution**: Use Prettier for formatting until ESLint config is migrated to v9

### Performance Expectations
- Frontend hot reload: ~1-2 seconds for most changes
- Frontend full rebuild: 3-4 minutes  
- Prettier formatting: 1-3 seconds for entire codebase