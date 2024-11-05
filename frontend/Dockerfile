# Base image
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy the package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install && \
    npm install sass sass-loader sass-embedded-linux-musl-x64 --save-dev

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