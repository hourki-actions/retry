FROM python:3.11-slim-buster

LABEL "maintainer"="hourki-actions"

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
ADD scripts /scripts
RUN chmod +x /scripts/entrypoint.py

CMD ["python", "/scripts/entrypoint.py"]
