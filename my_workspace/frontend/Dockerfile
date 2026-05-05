# ─── Stage 1: Build ──────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci

COPY . .
RUN npm run build

# ─── Stage 2: Serve via Nginx ────────────────────────────
# Vue SPA build output ถูก copy เข้า nginx image
# ใน docker-compose ให้ nginx build context include frontend dist
FROM scratch AS export
COPY --from=builder /app/dist /dist
