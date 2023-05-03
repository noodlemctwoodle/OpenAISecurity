FROM python:3.10

RUN apt-get update && apt-get install -y git

RUN mkdir -p /usr/src/rodbot
WORKDIR /usr/src/rodbot

COPY requirements.txt /usr/src/rodbot/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /usr/src/rodbot
RUN cp gui/application.py .

EXPOSE 8501

CMD ["streamlit", "run", "application.py"]