FROM node:26-alpine AS deps
WORKDIR /app
RUN chown node:node /app
USER node
COPY --chown=node:node package.json package-lock.json ./
RUN npm ci

FROM deps AS dev
COPY --chown=node:node . .
EXPOSE 5173
CMD ["npx", "vite", "--host", "0.0.0.0"]

FROM deps AS build
COPY --chown=node:node . .
RUN npm run build

FROM nginxinc/nginx-unprivileged:1.29-alpine AS prod
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8080
