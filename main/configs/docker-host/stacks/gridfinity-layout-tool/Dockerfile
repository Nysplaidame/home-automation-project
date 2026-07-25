# External Linux-builder recipe only. Do not run this build on VM 103.
ARG GRIDFINITY_VERSION=gridfinity-layout-tool-v4.253.0

FROM node:24-alpine AS build
ARG GRIDFINITY_VERSION
ENV NODE_OPTIONS=--max-old-space-size=1536
RUN apk add --no-cache git
RUN corepack enable && corepack prepare pnpm@11.2.2 --activate
WORKDIR /src
RUN git clone --depth 1 --branch "${GRIDFINITY_VERSION}" https://github.com/andymai/gridfinity-layout-tool.git .
RUN pnpm install --frozen-lockfile
RUN pnpm run build

FROM nginxinc/nginx-unprivileged:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /src/dist /usr/share/nginx/html
EXPOSE 8080
