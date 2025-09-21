# Base image
FROM node:24.3-alpine

# Set working directory
WORKDIR /app

# Pass environment variables as build args
ARG API_BASE_URL
ARG FASTAPI_API_TOKEN
ARG NUXT_SITE_URL
ARG NUXT_SITE_NAME
ARG NUXT_TURNSTILE_SITE_KEY
ARG NUXT_TURNSTILE_SECRET_KEY

ENV API_BASE_URL=$API_BASE_URL \
    FASTAPI_API_TOKEN=$FASTAPI_API_TOKEN \
    NUXT_SITE_URL=$NUXT_SITE_URL \
    NUXT_SITE_NAME=$NUXT_SITE_NAME \
    NUXT_TURNSTILE_SITE_KEY=$NUXT_TURNSTILE_SITE_KEY \
    NUXT_TURNSTILE_SECRET_KEY=$NUXT_TURNSTILE_SECRET_KEY \
    NODE_OPTIONS="--max_old_space_size=4096"

# Copy the package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm ci --legacy-peer-deps --prefer-offline --no-audit

# Copy project files
COPY . .

# Build the Nuxt app with increased memory limit
RUN NODE_OPTIONS="--max_old_space_size=4096" npm run build

# Remove dev dependencies for a smaller production image
RUN npm prune --production

# Expose the application port
EXPOSE 3000

# Command to run the app in production mode
CMD ["node", "--max_old_space_size=2048", "./.output/server/index.mjs"]
