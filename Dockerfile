FROM python:3.12
WORKDIR /python-app
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_APP=app.py
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
EXPOSE 5000
COPY . .
CMD ["flask","run"]