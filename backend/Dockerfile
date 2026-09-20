FROM node:20-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev)
RUN npm ci

# Copy Prisma schema and generate client
COPY prisma ./prisma/
RUN npx prisma generate

# Copy application code
COPY src ./src/
COPY tsconfig.json ./

# Build TypeScript
RUN npm run build

# Production stage
FROM node:20-alpine

# Install FFmpeg and runtime dependencies
RUN apk add --no-cache ffmpeg

WORKDIR /app

# Copy package files and install production dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy Prisma schema and generated client
COPY --from=builder /app/prisma ./prisma/
COPY --from=builder /app/node_modules/.prisma ./node_modules/.prisma
COPY --from=builder /app/node_modules/@prisma ./node_modules/@prisma

# Copy built application
COPY --from=builder /app/dist ./dist

# Create necessary directories
RUN mkdir -p /transcode

EXPOSE 3000

# Run migrations and start application (seed is included in migrations)
CMD ["sh", "-c", "npx prisma migrate deploy && node dist/index.js"]
