FROM bcgovimages/von-image:next-1

RUN pip install pynacl prometheus_client

ADD fetch_status.py .

CMD ["python", "fetch_status.py"]
