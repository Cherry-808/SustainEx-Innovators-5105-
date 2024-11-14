# 开发阶段
FROM node:16

WORKDIR /usr/src/app

# 复制依赖文件
COPY Back end.py

# 安装依赖
RUN npm install

# 复制源代码
COPY . . 

# 设置环境变量
ENV NODE_ENV=production
ENV PORT=3000
ENV MONGO_URI=mongodb://db:27017/myapp

EXPOSE 3000

CMD ["npm", "start"]