FROM node:24-alpine AS builder

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:mainline-alpine
COPY default.conf /etc/nginx/conf.d/
COPY --from=builder /app/dist/ /var/www/html/
