FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Expose port
EXPOSE 5173

# Run development server (for docker-compose)
# For production, uncomment build step and use: CMD ["npm", "run", "preview"]
CMD ["npm", "run", "dev", "--", "--host"]

