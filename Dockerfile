FROM python:3.10.16-bullseye

WORKDIR /app

COPY main.py .

COPY requirements.txt .

COPY ./src ./src

COPY .env  .

COPY system_prompt.json .

COPY system_prompt_summarize.json .

RUN pip3 install -r requirements.txt

EXPOSE 8080

CMD [ "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8080"]