# ============================================================
# Stage 1 — deps: Install dependencies only
# ============================================================
FROM node:20-alpine AS deps

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

# ============================================================
# Stage 2 — builder: Build Next.js application
# ============================================================
FROM node:20-alpine AS builder

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED=1

# Build arg: K8s service DNS name — baked into client bundle at build time
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Dummy build-time values — only needed for static analysis during build
# Actual secrets come from K8s Secrets at runtime
ARG DATABASE_URL="postgresql://placeholder:placeholder@placeholder/placeholder"
ENV DATABASE_URL=$DATABASE_URL
ARG BETTER_AUTH_SECRET="build-time-placeholder-secret-not-used-at-runtime"
ENV BETTER_AUTH_SECRET=$BETTER_AUTH_SECRET
ARG BETTER_AUTH_URL="http://localhost:3000"
ENV BETTER_AUTH_URL=$BETTER_AUTH_URL

RUN npx next build

# ============================================================
# Stage 3 — runner: Production image (minimal)
# ============================================================
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create non-root group and user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy standalone output from builder (requires output:'standalone' in next.config.ts)
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Run as non-root (Constitution Law XXIV — non-root containers)
USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD wget -qO- http://localhost:3000/ || exit 1

CMD ["node", "server.js"]
