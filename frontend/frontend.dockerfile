FROM node:16.14-slim as builder

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

ARG FRONTEND_APP="GreenPlum Permission Manager"
ENV VUE_APP_NAME=${FRONTEND_APP}

ARG FRONTEND_DOMAIN=localhost
ENV VUE_APP_DOMAIN=${FRONTEND_DOMAIN}

RUN npm run build

FROM nginx:1.19.8

LABEL maintainer="Ostap Konstantinov <konstantinov.ov@dns-shop.ru>"

COPY --from=builder /app/dist/ /usr/share/nginx/html
COPY ./nginx.conf /etc/nginx/conf.d/default.conf
COPY ./nginx-backend-not-found.conf /etc/nginx/extra-conf.d/backend-not-found.conf
