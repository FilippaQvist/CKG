#Download base image ubuntu
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND noninteractive
ENV LC_CTYPE en_US.UTF-8
ENV LANG en_US.UTF-8
ENV R_BASE_VERSION 3.6.1

MAINTAINER Alberto Santos "alberto.santos@cpr.ku.dk"

USER root

RUN apt-get update && \
    apt-get -yq dist-upgrade && \
    apt-get install -yq --no-install-recommends && \
    apt-get install -yq apt-utils software-properties-common && \
    apt-get install -yq locales && \
    apt-get install -yq wget && \
    apt-get install -yq unzip && \
    apt-get install -yq build-essential sqlite3 libsqlite3-dev libxml2 libxml2-dev zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libcurl4-openssl-dev && \
    apt-get install -yq nginx && \
    apt-get install -yq redis-server && \
    apt-get install -yq git && \
    apt-get -y install sudo && \
    rm -rf /var/lib/apt/lists/*

## User management
RUN adduser --quiet --disabled-password --shell /bin/bash --home /home/adminhub --gecos "User" adminhub && \
    echo "adminhub:adminhub" | chpasswd && \
    adduser --quiet --disabled-password --shell /bin/bash --home /home/ckguser --gecos "User" ckguser && \
    echo "ckguser:ckguser" | chpasswd && \
    adduser --disabled-password --gecos '' --uid 1500 nginx

# Python 3.6.8 installation
RUN wget https://www.python.org/ftp/python/3.6.8/Python-3.6.8.tgz
RUN tar -xzf Python-3.6.8.tgz
WORKDIR Python-3.6.8
RUN ./configure
RUN make altinstall
RUN make install
## pip upgrade
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py
RUN pip3 install --upgrade pip
RUN pip3 install setuptools

WORKDIR /

# Set the locale
RUN locale-gen en_US.UTF-8

# gpg key for cran updates
RUN gpg --keyserver keyserver.ubuntu.com --recv-keys E084DAB9 && \
    gpg -a --export E084DAB9 > cran.asc && \
    apt-key add cran.asc

RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 51716619E084DAB9   

RUN echo "deb https://cloud.r-project.org/bin/linux/ubuntu bionic-cran35/" > /etc/apt/sources.list.d/cran.list

# Installation openJDK 8
RUN add-apt-repository ppa:openjdk-r/ppa
RUN apt-get update
RUN apt-get install -yq openjdk-8-jdk
RUN java -version
RUN javac -version 

# NEO4J 3.5.14
RUN wget -O - https://debian.neo4j.com/neotechnology.gpg.key | apt-key add - && \
    echo "deb [trusted=yes] https://debian.neo4j.com stable 3.5" > /etc/apt/sources.list.d/neo4j.list && \
    apt-get update && \
    apt-get install -yq neo4j=1:3.5.20

## Setup initial user Neo4j
RUN rm -f /var/lib/neo4j/data/dbms/auth && \
    neo4j-admin set-initial-password "NeO4J"

## Install graph data science library and APOC
RUN wget -P /var/lib/neo4j/pubgins https://github.com/neo4j/graph-data-science/releases/download/1.1.5/neo4j-graph-data-science-1.1.5-standalone.jar
RUN wget -P /var/lib/neo4j/plugins https://github.com/neo4j-contrib/neo4j-apoc-procedures/releases/download/3.5.0.15/apoc-3.5.0.15-all.jar

RUN ls -lrth /var/lib/neo4j/plugins

## Change configuration
RUN cat /etc/neo4j/neo4j.conf
COPY /resources/neo4j_db/neo4j.conf  /etc/neo4j/.

## Test the service Neo4j
RUN service neo4j start && \
    sleep 30 && \
    service neo4j stop && \
    cat /var/log/neo4j/neo4j.log

## Load backup with Clinical Knowledge Graph
RUN mkdir -p /var/lib/neo4j/data/backup
#RUN wget -O /var/lib/neo4j/data/backup/ckg_201020_neo4j_3.5.20.dump https://data.mendeley.com/public-files/datasets/mrcf7f4tc2/files/e454e520-2384-49ee-ac41-d4fbfa15c065/file_downloaded
COPY /resources/neo4j_db/ckg_201020_neo4j_3.5.20.dump /var/lib/neo4j/data/backup/.
RUN mkdir -p /var/lib/neo4j/data/databases/graph.db
RUN sudo -u neo4j neo4j-admin load --from=/var/lib/neo4j/data/backup/ckg_201020_neo4j_3.5.20.dump --database=graph.db --force

## Remove dump file
RUN echo "Done with restoring backup, removing backup folder"
RUN rm -rf /var/lib/neo4j/data/backup

#RUN ls -lrth  /var/lib/neo4j/data/databases
RUN [ -e  /var/lib/neo4j/data/databases/store_lock ] && rm /var/lib/neo4j/data/databases/store_lock

# R
RUN apt-get update && \
    apt-get install -y --no-install-recommends \ 
    littler \
    r-cran-littler \
    r-base=${R_BASE_VERSION}* \
    r-base-dev=${R_BASE_VERSION}* \
    r-recommended=${R_BASE_VERSION}* && \
    echo 'options(repos = c(CRAN = "https://cloud.r-project.org/"), download.file.method = "libcurl")' >> /etc/R/Rprofile.site
    
## Install packages
COPY /resources/R_packages.R /R_packages.R
RUN Rscript R_packages.R

# START neo4j
RUN service neo4j start

# Python
## Copy Requirements
COPY ./requirements.txt /requirements.txt

## Install Python libraries
RUN pip3 install --ignore-installed -r requirements.txt

#Creating CKG directory and setting up CKG
RUN mkdir /CKG
COPY --chown=nginx src /CKG/src
COPY docker_entrypoint.sh /CKG/.
ENV PYTHONPATH "${PYTHONPATH}:/CKG/src"

RUN echo "Setting up the config files"
COPY setup_CKG.py /CKG/.
COPY setup_config_files.py /CKG/.
RUN python3 /CKG/setup_CKG.py
RUN python3 /CKG/setup_config_files.py
RUN chown -R nginx /CKG

RUN echo "Creating Test user in the database"
RUN python3 /CKG/src/graphdb_builder/builder/create_user.py -u test_user -d test_user -n test -e test@ckg.com -a test

RUN service neo4j stop
#RUN [ -e  /var/lib/neo4j/data/databases/store_lock ] && rm /var/lib/neo4j/data/databases/store_lock

# JupyterHub
RUN apt-get -y install npm nodejs && \
    npm install -g configurable-http-proxy
    
RUN pip3 install jupyterhub && \
    pip3 install --upgrade notebook

RUN mkdir /etc/jupyterhub
COPY /resources/jupyterhub.py /etc/jupyterhub/.
RUN cp -r /CKG/src/notebooks /home/adminhub/.
RUN cp -r /CKG/src/notebooks /home/ckguser/.
RUN chown -R adminhub /home/adminhub/notebooks
RUN chown -R ckguser /home/ckguser/notebooks

RUN ls -alrth /home/ckguser
RUN ls -alrth /home/ckguser/notebooks

# NGINX and UWSGI
## Copy configuration file
COPY /resources/nginx.conf /etc/nginx/.

RUN chmod 777 /run/ -R && \
    chmod 777 /root/ -R

## Install uWSGI
RUN pip3 install uwsgi

## Copy the base uWSGI ini file
COPY /resources/uwsgi.ini /etc/uwsgi/apps-available/uwsgi.ini
COPY /resources/uwsgi.ini /etc/uwsgi/apps-enabled/uwsgi.ini


## Create log directory
RUN mkdir -p /var/log/uwsgi

# Remove apt cache to make the image smaller
RUN rm -rf /var/lib/apt/lists/*

RUN chmod +x /CKG/docker_entrypoint.sh

RUN ls -alrth /
RUN ls -alrth /CKG
RUN ls -alrth /CKG/src/notebooks
# Expose ports (HTTP Neo4j, Bolt Neo4j, jupyterHub, CKG prod, CKG dev, Redis)
EXPOSE 7474 7687 8090 8050 5000 6379

ENTRYPOINT [ "/bin/bash", "/CKG/docker_entrypoint.sh"]
