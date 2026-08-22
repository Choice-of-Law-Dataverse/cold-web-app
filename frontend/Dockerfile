# ============================================
# Build Stage
# ============================================
FROM node:22.18-alpine AS builder

# Public site URL is needed at build time by sitemap/robots
ARG NUXT_SITE_URL

# Set working directory
WORKDIR /app

# Copy package manifest, lockfile and pnpm settings (pnpm 11 reads settings from pnpm-workspace.yaml)
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./

# Activate the pnpm version pinned in package.json's packageManager field
RUN corepack enable pnpm && corepack install

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy project files
COPY . .

# Set environment variables for build
ENV NUXT_SITE_URL=$NUXT_SITE_URL

# Build the Nuxt app with increased memory limit
RUN NODE_OPTIONS="--max_old_space_size=4096" pnpm run build

# ============================================
# Production Stage - No secrets, only output
# ============================================
FROM node:22.18-alpine

WORKDIR /app

# Nuxt's .output is self-contained (Nitro bundles all server deps),
# so no extra `pnpm install` is needed in this stage.
COPY --from=builder /app/.output ./.output

ENV NODE_ENV=production
EXPOSE 3000

CMD ["node", "--max_old_space_size=2048", "./.output/server/index.mjs"]
