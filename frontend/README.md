# Frontend - Nuxt 3 Application

Nuxt 3 frontend for the Choice of Law Dataverse (CoLD), built with Vue.js, TypeScript, and TailwindCSS.

> **For AI coding agents**: See [AGENTS.md](AGENTS.md) for agent-specific instructions.

## Prerequisites

- **Node.js v20+** (tested with v20.19.5)
- **npm 10+** (tested with v10.8.2)

## Setup

Install dependencies:

```bash
npm install
```

## Development

Start the development server on `http://localhost:3000`:

```bash
npm run dev
```

## Production

Build the application for production:

```bash
npm run build
```

Preview the production build:

```bash
npm run preview
```

## Before Committing

**Always run the validation checks:**

```bash
npm run check
```

This command runs:

- **Build validation**: Ensures the application builds successfully
- **Prettier**: Checks code formatting
- **Linting**: Runs ESLint for code quality

Individual validation commands:

```bash
npm run format:check  # Check formatting
npm run format        # Fix formatting
npm run lint          # Check for issues
npm run lint:fix      # Fix issues automatically
npm run build         # Verify build works
```

## Code Standards

- **TypeScript only**: Use `.ts` and `.vue` files with `<script setup lang="ts">`, never `.js`
- **Composition API**: Use Vue Composition API with composables
- **No barrel files**: Import directly from specific modules
- **Conventional commits**: Follow semantic commit format

See [AGENTS.md](AGENTS.md) for detailed coding conventions.

Check out the [Nuxt 3 documentation](https://nuxt.com/docs/getting-started/introduction) and [deployment documentation](https://nuxt.com/docs/getting-started/deployment) for more information.

## Additional Resources

### Docker (Production Only)

**Docker is only used for production deployment. Local and agentic development should use npm directly.**

For production deployment:

```bash
docker build -t cold-nuxt-frontend .
docker run -p 3000:3000 cold-nuxt-frontend
```

### Nuxt Leaflet

Resources for landing page map:

- https://nuxt.com/modules/leaflet
- Interactive Choropleth Map: https://leafletjs.com/examples/choropleth/
- https://leafletjs.com/reference.html
- https://github.com/vue-leaflet/vue-leaflet/issues/153
- https://stackoverflow.com/a/54857289/22393957
- https://leaflet-extras.github.io/leaflet-providers/preview/
- GeoJSON country vector maps: https://geojson-maps.kyd.au/
