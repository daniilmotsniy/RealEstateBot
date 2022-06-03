FROM python:3.9

RUN mkdir /src
WORKDIR /src
COPY . /src
RUN pip install -r requirements.txt
RUN pip install "pymongo[srv]"
RUN pybabel extract --input-dirs=. -o locales/bot.pot --version=2.2 --project=AvezorBot -k __:1,2 && pybabel update -d locales -D bot -i locales/bot.pot
RUN pybabel compile -d locales -D bot

ARG MONGODB_URL
ARG BOT_TOKEN

ENV MONGODB_URL $MONGODB_URL
ENV BOT_TOKEN $BOT_TOKEN

RUN python run.py

EXPOSE 80
