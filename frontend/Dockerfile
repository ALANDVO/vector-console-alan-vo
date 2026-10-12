FROM node:24-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:24-alpine

WORKDIR /app

RUN npm install -g serve && \
    addgroup -g 10001 appgroup && \
    adduser -u 10001 -G appgroup -s /bin/sh -D appuser

USER appuser

COPY --from=builder --chown=appuser:appgroup /app/dist /app/dist

EXPOSE 3000

CMD ["serve", "-s", "/app/dist", "-l", "3000"]
