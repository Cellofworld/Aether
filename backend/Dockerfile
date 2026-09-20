FROM node:20-alpine

# Install FFmpeg and other dependencies
RUN apk add --no-cache ffmpeg

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy Prisma schema and generate client
COPY prisma ./prisma/
RUN npx prisma generate

# Copy application code
COPY src ./src/
COPY tsconfig.json ./

# Build TypeScript
RUN npm run build

# Create necessary directories
RUN mkdir -p /transcode

EXPOSE 3000

CMD ["sh", "-c", "npx prisma migrate deploy && node dist/index.js"]
