# Nuxt 4 Frontend Application

Look at the [Nuxt 4 documentation](https://nuxt.com/docs/getting-started/introduction) to learn more.

## Requirements

- Node.js v20.5.0 or higher (currently tested with v20.19.5)
- npm 10.x or higher

## Setup

Make sure to install the dependencies:

```bash
# npm
npm install

# pnpm
pnpm install

# yarn
yarn install

# bun
bun install
```

## Technology Stack

This application runs on:
- **Nuxt 4.1.2** - Latest Nuxt framework
- **Tailwind CSS v4.1.13** - Latest Tailwind with built-in features
- **@nuxt/ui v3.3.4** - Modern UI components
- **Vue 3** - Latest Vue framework

## Development Server

Start the development server on `http://localhost:3000`:

```bash
# npm
npm run dev

# pnpm
pnpm run dev

# yarn
yarn dev

# bun
bun run dev
```

## Production

Build the application for production:

```bash
# npm
npm run build

# pnpm
pnpm run build

# yarn
yarn build

# bun
bun run build
```

Locally preview production build:

```bash
# npm
npm run preview

# pnpm
pnpm run preview

# yarn
yarn preview

# bun
bun run preview
```

Check out the [deployment documentation](https://nuxt.com/docs/getting-started/deployment) for more information.

# Docker

## Building and Running the Container

To build the container run:
`docker build -t cold-nuxt-frontend .`
To run the container run:
`docker run -p 3000:3000 cold-nuxt-frontend`

The docker image has been pushed to dockerhub using:
`docker tag cold-nuxt-frontend simonweigold/cold-nuxt-frontend:latest`
`docker push simonweigold/cold-nuxt-frontend:latest`

# Migration to Nuxt v4

This application has been successfully migrated from Nuxt 3 to Nuxt 4.1.2, coordinated with the Tailwind v4 migration.

## What Changed
- **Framework**: Nuxt 3.12.4 → Nuxt 4.1.2
- **CSS Framework**: Tailwind CSS v3 → v4.1.13 with `@import "tailwindcss"`
- **UI Library**: @nuxt/ui v2 → v3.3.4
- **Modules**: Updated to Nuxt v4 compatible versions

## Temporarily Disabled Modules
- `nuxt-purgecss` - Awaiting Nuxt v4 compatibility
- `nuxt-plotly` - Awaiting Nuxt v4 compatibility

These modules will be re-enabled when Nuxt v4 compatible versions are available.

# Nuxt Leaflet

Resources for landing page map:

- https://nuxt.com/modules/leaflet
- Interactive Choropleth Map: https://leafletjs.com/examples/choropleth/
- https://leafletjs.com/reference.html
- https://github.com/vue-leaflet/vue-leaflet/issues/153
- https://stackoverflow.com/a/54857289/22393957
- https://leaflet-extras.github.io/leaflet-providers/preview/
- GeoJSON country vector maps: https://geojson-maps.kyd.au/
