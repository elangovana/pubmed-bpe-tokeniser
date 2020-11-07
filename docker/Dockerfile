FROM python:3.7

# Install requirements
COPY ./src/requirements.txt  /tmp

RUN pip install -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Copy code
RUN mkdir -p /code
COPY ./src   /code

ENV PYTHONPATH=/code

ENTRYPOINT ["python3"]