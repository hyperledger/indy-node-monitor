FROM python:3.12-slim-bullseye

ARG uid=1001
ARG user=indy
ARG tag_name=indy-node-monitor
ARG tag_version=

ENV HOME="/home/$user" \
    APP_ROOT="$HOME" \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    PIP_NO_CACHE_DIR=off \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8 \
    RUST_LOG=warning \
    SHELL=/bin/bash \
    SUMMARY="Indy Node Monitor" \
    DESCRIPTION="A container for monitoring the nodes of an Indy Node network."

LABEL summary="$SUMMARY" \
      description="$DESCRIPTION" \
      io.k8s.description="$DESCRIPTION" \
      io.k8s.display-name="$tag_name $tag_version" \
      name="$tag_name" \
      version="$tag_version" \
      maintainer=""

# Add local binaries and aliases to path
ENV PATH="$HOME/.local/bin:$PATH"

# Make libraries resolvable by python
ENV LD_LIBRARY_PATH="$HOME/.local/lib:$LD_LIBRARY_PATH"
RUN echo "$HOME/.local/lib" > /etc/ld.so.conf.d/local.conf && ldconfig

# Add indy user
RUN useradd -U -ms /bin/bash -u $uid $user
WORKDIR $HOME

# - In order to drop the root user, we have to make some directories writable
#   to the root group as OpenShift default security model is to run the container
#   under random UID.
RUN usermod -a -G root $user

# Create standard directories to allow volume mounting and set permissions
# Note: PIP_NO_CACHE_DIR environment variable should be cleared to allow caching
RUN mkdir -p \
    $HOME/log \
    $HOME/cache \
    $(python -m site --user-site)

# The root group needs access the directories under $HOME for the container to function in OpenShift.
# Also ensure the permissions on the python 'site-packages' folder are set correctly.
RUN chown -R $user:root $HOME && \
    chmod -R ug+rw $HOME $HOME/log $HOME/cache && \
    chmod +rx $(python -m site --user-site)

USER $user

ADD requirements.txt .
RUN pip3 install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

ADD networks.json .
ADD *.py ./
ADD plugins ./plugins

ENTRYPOINT ["bash", "-c", "python main.py $@", "--"]
