FROM bcgovimages/von-image:next-1

RUN pip install pynacl

ADD fetch_status.py .

ENTRYPOINT ["bash", "-c", "python fetch_status.py $@", "--"]
