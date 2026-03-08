# ============================================
# Build Stage - Contains secrets (discarded)
# ============================================
FROM node:22.18-alpine AS builder

# Build arguments for Auth0 configuration
ARG AUTH0_AUDIENCE
ARG AUTH0_CLIENT_ID
ARG AUTH0_CLIENT_SECRET
ARG AUTH0_SECRET
ARG NUXT_SITE_URL

# Set working directory
WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy package manifest and lockfile
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy project files
COPY . .

# Set environment variables for build
ENV AUTH0_AUDIENCE=$AUTH0_AUDIENCE \
    AUTH0_CLIENT_ID=$AUTH0_CLIENT_ID \
    AUTH0_CLIENT_SECRET=$AUTH0_CLIENT_SECRET \
    AUTH0_SECRET=$AUTH0_SECRET \
    NUXT_SITE_URL=$NUXT_SITE_URL

# Build the Nuxt app with increased memory limit
RUN NODE_OPTIONS="--max_old_space_size=4096" pnpm run build

# ============================================
# Production Stage - No secrets, only output
# ============================================
FROM node:22.18-alpine

# Set working directory
WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy package manifest and lockfile
COPY package.json pnpm-lock.yaml ./

# Install only production dependencies
RUN pnpm install --frozen-lockfile --prod

# Copy built application from builder stage
# This excludes all build-time secrets and source code
COPY --from=builder /app/.output ./.output

# Expose the application port
EXPOSE 3000

# Command to run the app in production mode
CMD ["node", "--max_old_space_size=2048", "./.output/server/index.mjs"]
