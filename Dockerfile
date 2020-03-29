# NOTE: Only use this when you want to build image locally
#       else use `docker pull bcsecurity/empire:{VERSION}`
#       all image versions can be found at: https://hub.docker.com/r/bcsecurity/empire/

# -----BUILD COMMANDS----
# 1) build command: `docker build -t bcsecurity/empire .`
# 2) create volume storage: `docker create -v /empire --name data bcsecurity/empire`
# 3) run out container: `docker run -ti --volumes-from data bcsecurity/empire /bin/bash`

# -----RELEASE COMMANDS----
# Handled by GitHub Actions

# -----BUILD ENTRY-----

# image base
FROM python:3.7.5-buster

# extra metadata
LABEL maintainer="bc-security"
LABEL description="Dockerfile base for Empire server."

# env setup
ENV STAGING_KEY=RANDOM
ENV DEBIAN_FRONTEND=noninteractive

# set the def shell for ENV
SHELL ["/bin/bash", "-c"]

RUN apt-get update && \
      apt-get -y install \
        sudo \
        lsb-release \
	    make \
	    g++ \
	    python-dev \
	    python-m2crypto \
	    swig \
	    python-pip \
	    libxml2-dev \
	    default-jdk \
	    libffi-dev \
	    libssl1.1 \
	    libssl-dev \
	    build-essential \
	    apt-transport-https \
	    curl \
	    gnupg

RUN curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add - && \
	sudo sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/microsoft-debian-stretch-prod stretch main" > /etc/apt/sources.list.d/microsoft.list' && \
    mkdir /tmp/pwshtmp && \
    (cd /tmp/pwshtmp && \
        wget http://http.us.debian.org/debian/pool/main/i/icu/libicu57_57.1-6+deb9u3_amd64.deb && \
        wget http://http.us.debian.org/debian/pool/main/u/ust/liblttng-ust0_2.9.0-2+deb9u1_amd64.deb && \
        wget http://http.us.debian.org/debian/pool/main/libu/liburcu/liburcu4_0.9.3-1_amd64.deb && \
        wget http://http.us.debian.org/debian/pool/main/u/ust/liblttng-ust-ctl2_2.9.0-2+deb9u1_amd64.deb && \
        wget http://security.debian.org/debian-security/pool/updates/main/o/openssl1.0/libssl1.0.2_1.0.2u-1~deb9u1_amd64.deb && \
        sudo dpkg -i *.deb) && \
		rm -rf /tmp/pwshtmp && \
		sudo apt-get update && \
		sudo apt-get install -y powershell

WORKDIR /empire

RUN pip install pipenv

COPY Pipfile /empire
COPY Pipfile.lock /empire

RUN pipenv install

COPY . /empire

RUN rm ./data/empire.db

RUN ./cert.sh

CMD ["pipenv", "run", "python", "empire"]
