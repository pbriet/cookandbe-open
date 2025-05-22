#### Base image

FROM public.ecr.aws/bitnami/node:18 as base

RUN mkdir /app/public /app/src /docker

COPY .browserslistrc .eslintrc.js .prettierrc babel.config.js package.json vue.config.js yarn.lock /app/

WORKDIR /app

RUN yarn install

ENV NODE_OPTIONS='--openssl-legacy-provider'

COPY .env.* /app/
COPY entrypoint.sh /docker/
COPY public/ /app/public/
COPY src/ /app/src/


#### Development - not compiling
FROM base as development

ENTRYPOINT ["/docker/entrypoint.sh"]
CMD ["/bin/bash", "-c", "npm run serve"]

EXPOSE 8080

#### Build
ARG BUILD_ENV
FROM base as build
ARG BUILD_ENV
RUN /app/node_modules/.bin/vue-cli-service build --mode=${BUILD_ENV}

#### Static serve of built assets
FROM public.ecr.aws/nginx/nginx:1.25-alpine as production

COPY --from=build /app/dist /usr/share/nginx/html
COPY deploy-assets/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
