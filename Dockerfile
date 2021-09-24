FROM jemand771/chromedriver-base-python

WORKDIR /tmp
COPY requirements.txt .
RUN pip3 install -r requirements.txt

WORKDIR /app
COPY *.py .

CMD ["python3", "app.py"]
