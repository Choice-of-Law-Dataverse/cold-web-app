# Use an official Node.js runtime as a parent image
FROM node:18 AS build-stage

# Set the working directory inside the container
WORKDIR /app

# Copy the package.json and package-lock.json files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the Vue.js app
RUN npm run build

# Use a minimal Nginx image to serve the static files
FROM nginx:stable-alpine AS production-stage

# Copy the build output from the previous stage to the Nginx html folder
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
