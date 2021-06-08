FROM bcgovimages/von-image:next-1

ARG user=indy
USER root
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    python3-dev && \
    rm -rf /var/lib/apt/lists/*
USER $user

RUN pip install pynacl gspread oauth2client

USER $user

ADD requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ADD networks.json .
ADD *.py ./

ENTRYPOINT ["bash", "-c", "python fetch_status.py $@", "--"]