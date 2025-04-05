FROM node:alpine

WORKDIR /app

COPY package.json ./

RUN npm install

COPY . .

EXPOSE 5173

# Command to run the app
CMD ["npm", "run", "dev"]