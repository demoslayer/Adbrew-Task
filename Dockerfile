# set base image (host OS)
FROM python:3.8

RUN rm /bin/sh && ln -s /bin/bash /bin/sh

RUN apt-get -y update
RUN apt-get install -y curl nano wget nginx git

RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list


# Install Node.js 16 FIRST (required for react-scripts 4.0.1)
# Install before MongoDB to avoid dependency conflicts
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && \
    apt-get install -y nodejs

# Install Yarn
RUN apt-get install -y yarn

# Mongo
RUN ln -s /bin/echo /bin/systemctl

# Install libssl1.1 which is required by MongoDB 4.4
# First try to install from available repos, then fall back to manual download
RUN (apt-get install -y libssl1.1 2>/dev/null || \
     (curl -L -o /tmp/libssl1.1.deb http://archive.debian.org/debian/pool/main/o/openssl1.0/libssl1.1_1.1.1n-0+deb10u4_amd64.deb 2>/dev/null || \
      curl -L -o /tmp/libssl1.1.deb http://ftp.debian.org/debian/pool/main/o/openssl1.0/libssl1.1_1.1.1n-0+deb10u4_amd64.deb 2>/dev/null || \
      curl -L -o /tmp/libssl1.1.deb http://snapshot.debian.org/archive/debian/20221201T201352Z/pool/main/o/openssl1.0/libssl1.1_1.1.1n-0+deb10u4_amd64.deb 2>/dev/null) && \
     test -f /tmp/libssl1.1.deb && \
     dpkg -i /tmp/libssl1.1.deb 2>&1 || true && \
     apt-get install -f -y && \
     rm -f /tmp/libssl1.1.deb)

# Add MongoDB repository and install MongoDB
# Install MongoDB AFTER Node.js to avoid breaking Node.js installation
RUN wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | apt-key add -
RUN echo "deb http://repo.mongodb.org/apt/debian buster/mongodb-org/4.4 main" | tee /etc/apt/sources.list.d/mongodb-org-4.4.list
RUN apt-get -y update
# Install MongoDB packages directly with dpkg to bypass apt's dependency check
# Download packages and install with force-depends, then mark as manually installed to prevent removal
RUN cd /tmp && \
    apt-get download mongodb-org mongodb-org-server mongodb-org-mongos mongodb-org-shell mongodb-org-tools && \
    dpkg --force-depends -i *.deb 2>&1 || true && \
    apt-mark hold mongodb-org mongodb-org-server mongodb-org-mongos mongodb-org-shell mongodb-org-tools && \
    apt-get install -y mongodb-database-tools mongodb-org-database-tools-extra 2>&1 || true && \
    rm -f *.deb

# Install compatible pip version (pip < 24.1 needed for celery==5.0.5 metadata)
RUN pip install "pip<24.1"


ENV ENV_TYPE staging
ENV MONGO_HOST mongo
ENV MONGO_PORT 27017
##########

ENV PYTHONPATH=$PYTHONPATH:/src/

# copy the dependencies file to the working directory
COPY src/requirements.txt .

# install dependencies
RUN pip install -r requirements.txt
