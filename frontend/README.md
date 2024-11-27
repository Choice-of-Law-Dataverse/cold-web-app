# Nuxt 3 Minimal Starter

Look at the [Nuxt 3 documentation](https://nuxt.com/docs/getting-started/introduction) to learn more.

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

# Nuxt Leaflet

Resources for landing page map:

- https://nuxt.com/modules/leaflet
- Interactive Choropleth Map: https://leafletjs.com/examples/choropleth/
- https://leafletjs.com/reference.html
- https://github.com/vue-leaflet/vue-leaflet/issues/153
- https://stackoverflow.com/a/54857289/22393957
- https://leaflet-extras.github.io/leaflet-providers/preview/
