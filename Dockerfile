FROM python:3.11-alpine

LABEL "maintainer"="hourki-actions"

COPY requirements.txt requirements.txt
RUN python -m pip install --upgrade pip
RUN pip install numpy==1.22.3
RUN pip install -r requirements.txt
ADD scripts /scripts
RUN chmod +x /scripts/entrypoint.py

CMD ["python", "/scripts/entrypoint.py"]
