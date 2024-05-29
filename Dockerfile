FROM ubuntu:22.04


RUN apt update \
    && apt install -y \
        python3 \
        python3-pip \
        git \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip && pip3 install tox

WORKDIR /code
COPY . .
RUN pip3 install -e .

ENTRYPOINT ["/code/entrypoint.sh"]