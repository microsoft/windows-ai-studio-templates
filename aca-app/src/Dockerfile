FROM node:20.5.0
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv

WORKDIR /code
RUN python3 -m venv .env
COPY requirements.txt .
RUN .env/bin/python -m pip install --no-cache-dir -r requirements.txt
RUN npm install -g --prefix ./.mcp @modelcontextprotocol/server-filesystem
RUN mkdir .working
COPY . .
EXPOSE 8080
CMD [".env/bin/python", "app/mcp_chat.py"]