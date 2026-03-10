# ==============================================
# Todo AI Chatbot - Frontend Dockerfile
# Multi-stage build for Next.js 15
# ==============================================

# ---------------------------------------------
# Stage 1: Install all dependencies (for build)
# ---------------------------------------------
FROM node:20-alpine AS deps
WORKDIR /app

# Required for Next.js SWC on Alpine (musl libc compat)
RUN apk add --no-cache libc6-compat

# Copy package files
COPY package.json package-lock.json ./

# Install ALL dependencies (including devDependencies for build)
RUN npm ci

# ---------------------------------------------
# Stage 2: Build application
# ---------------------------------------------
FROM node:20-alpine AS builder
WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Set build-time environment variables
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production
ENV DOCKER_BUILD=true

# Build the Next.js application
RUN npm run build

# ---------------------------------------------
# Stage 3: Production runner
# ---------------------------------------------
FROM node:20-alpine AS runner
WORKDIR /app

# Create non-root user for security
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Set environment
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Copy built application from builder stage
# The standalone output includes server.js and necessary node_modules
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

# Change ownership to non-root user
RUN chown -R nextjs:nodejs /app

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Start the application
CMD ["node", "server.js"]
