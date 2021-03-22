FROM bcgovimages/von-image:next-1

RUN pip install pynacl gspread oauth2client

ADD networks.json .
ADD *.py ./

ENTRYPOINT ["bash", "-c", "python fetch_status.py $@", "--"]