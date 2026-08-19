# External Linux-builder recipe only. Do not run this build on VM 103.
ARG GRIDFINITY_VERSION=gridfinity-layout-tool-v4.342.0

FROM node:24-alpine@sha256:d32cdf619f63fe0471182d08996dd516c6275bb5fd31ae06e55a570bd9e1ad43 AS build
ARG GRIDFINITY_VERSION
ENV NODE_OPTIONS=--max-old-space-size=1536
RUN apk add --no-cache git
RUN corepack enable && corepack prepare pnpm@11.2.2 --activate
WORKDIR /src
RUN git clone --depth 1 --branch "${GRIDFINITY_VERSION}" https://github.com/andymai/gridfinity-layout-tool.git .
RUN pnpm install --frozen-lockfile
RUN pnpm run build

FROM nginxinc/nginx-unprivileged:alpine@sha256:334d92979f15aaecd5dd50af5105e1230e2bb70765d45b1e2f964e7c5eda81c3
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /src/dist /usr/share/nginx/html
EXPOSE 8080
