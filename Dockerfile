# Stage 1: Build the front end
FROM node:19 as build

WORKDIR /app

COPY ./web/package.json ./web/package-lock.json ./

RUN npm install

COPY ./web/ ./
RUN npm run build

# Stage 2: Set up the back end
FROM node:19

WORKDIR /app

COPY ./ ./
RUN npm install

COPY --from=build /app/dist ./dist

ENV NODE_ENV=production

EXPOSE 4200
CMD [ "node", "app.js" ]