# Base image
FROM node:18-alpine

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
    NUXT_TURNSTILE_SECRET_KEY=$NUXT_TURNSTILE_SECRET_KEY

# Copy the package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install --legacy-peer-deps && \
    npm install sass sass-loader sass-embedded-linux-musl-x64 --save-dev  --legacy-peer-deps

# Copy project files
COPY . .

# Build the Nuxt app
RUN npm run build

# Remove dev dependencies for a smaller production image
RUN npm prune --production

# Expose the application port
EXPOSE 3000

# Command to run the app in production mode
CMD ["node", "./.output/server/index.mjs"]
