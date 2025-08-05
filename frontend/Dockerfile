# frontend/Dockerfile
# This Dockerfile creates a production-ready build of the React app
# and serves it using a lightweight Nginx web server.

# --- Stage 1: Build the React application ---
# We use a specific version of Node.js for consistency. 'alpine' is a lightweight version.
FROM node:18-alpine AS builder

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json to leverage Docker's layer caching.
# This step only re-runs if these files change.
COPY package*.json ./

# Install all project dependencies
RUN npm install

# Copy the rest of the application source code into the container
COPY . .

# --- FIX: Grant execute permissions ---
# This command recursively adds execute permissions to the .bin directory
# within node_modules, which is where react-scripts lives. This resolves
# the "Permission denied" error during the build process.
RUN chmod +x -R ./node_modules/.bin

# Build the React application for production. This creates an optimized
# 'build' folder with static HTML, CSS, and JS files.
RUN npm run build


# --- Stage 2: Serve the application with Nginx ---
# We use a lightweight and stable version of Nginx.
FROM nginx:stable-alpine

# Copy the static files from the build stage into the Nginx server's public directory.
COPY --from=builder /app/build /usr/share/nginx/html

# Copy our custom Nginx configuration file. This is crucial for
# handling client-side routing in a Single Page Application (SPA).
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80, which is the default port for the Nginx server.
EXPOSE 80

# The command to start the Nginx server in the foreground when the container launches.
CMD ["nginx", "-g", "daemon off;"]
