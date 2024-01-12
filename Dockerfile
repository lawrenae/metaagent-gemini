# Use a base image with Python3.9 and Nodejs20 slim version
FROM nikolaik/python-nodejs:python3.9-nodejs20-slim

# Install Debian software needed by MetaGemini and clean up in one RUN command to reduce image size
RUN apt update &&\
    apt install -y gcc git chromium libjpeg-dev zlib1g-dev fonts-ipafont-gothic fonts-wqy-zenhei fonts-thai-tlwg fonts-kacst fonts-freefont-ttf libxss1  python3-dev python3-setuptools supervisor --no-install-recommends &&\
    apt clean && rm -rf /var/lib/apt/lists/*

# Install Mermaid CLI globally
ENV CHROME_BIN="/usr/bin/chromium" \
    PUPPETEER_CONFIG="/app/metagpt/config/puppeteer-config.json"\
    PUPPETEER_SKIP_CHROMIUM_DOWNLOAD="true"
RUN npm install -g @mermaid-js/mermaid-cli &&\
    npm cache clean --force

# copy our script
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# make them executable
#RUN sudo chmod +x /usr/src/app/scripts/*.sh


# Install Python dependencies and install MetaGemini
COPY . /app/metagpt
WORKDIR /app/metagpt
RUN mkdir workspace &&\
    pip install --no-cache-dir -r requirements.txt &&\
    pip install -e. --user

EXPOSE 8501

CMD ["/usr/bin/supervisord"]



