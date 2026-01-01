# Base image
FROM node:22-alpine

# Build arguments for Auth0 configuration
ARG AUTH0_AUDIENCE
ARG AUTH0_CLIENT_ID
ARG AUTH0_CLIENT_SECRET
ARG AUTH0_SECRET
ARG NUXT_SITE_URL

# Set working directory
WORKDIR /app

# Copy the package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm ci --legacy-peer-deps --prefer-offline --no-audit

# Copy project files
COPY . .

# Set environment variables for build
ENV AUTH0_AUDIENCE=$AUTH0_AUDIENCE \
    AUTH0_CLIENT_ID=$AUTH0_CLIENT_ID \
    AUTH0_CLIENT_SECRET=$AUTH0_CLIENT_SECRET \
    AUTH0_SECRET=$AUTH0_SECRET \
    NUXT_SITE_URL=$NUXT_SITE_URL

# Build the Nuxt app with increased memory limit
RUN NODE_OPTIONS="--max_old_space_size=4096" npm run build

# Remove dev dependencies for a smaller production image
RUN npm prune --production

# Expose the application port
EXPOSE 3000

# Command to run the app in production mode
CMD ["node", "--max_old_space_size=2048", "./.output/server/index.mjs"]
