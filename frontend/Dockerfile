FROM alpine:3.11.6 as builder

RUN apk update && apk add nodejs yarn
COPY package.json .
RUN yarn install --no-optional
COPY . .
RUN yarn build-production

FROM nginx:mainline-alpine
COPY default.conf /etc/nginx/conf.d/
COPY --from=builder dist/* /var/www/html/
