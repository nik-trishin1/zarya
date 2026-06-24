FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# Production build uses same-origin /api (nginx proxies to backend)
ARG VITE_API_URL=
ENV VITE_API_URL=$VITE_API_URL

# Bot username for share deep links (baked into JS at build time)
ARG VITE_BOT_USERNAME=zarya_friends_bot
ENV VITE_BOT_USERNAME=$VITE_BOT_USERNAME

ARG VITE_BOT_APP_SHORT_NAME=
ENV VITE_BOT_APP_SHORT_NAME=$VITE_BOT_APP_SHORT_NAME

RUN npm run build

FROM nginx:alpine

RUN apk add --no-cache gettext

COPY nginx.conf.template /etc/nginx/nginx.conf.template
COPY start.sh /start.sh
RUN chmod +x /start.sh && rm -f /etc/nginx/conf.d/default.conf

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80 8080

ENTRYPOINT ["/start.sh"]
