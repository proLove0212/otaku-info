FROM ubuntu:20.04
MAINTAINER Hermann Krumrey <hermann@krumreyh.com>

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && \
    apt install -y python3 python3-pip python3-psycopg2 git \
    ruby-sass npm yui-compressor && \
    pip3 install flask

RUN git clone https://gitlab.namibsun.net/namibsun/python/bokkichat -b develop && cd bokkichat && python3 setup.py install
RUN git clone https://gitlab.namibsun.net/namibsun/python/jerrycan -b develop && cd jerrycan &&  python3 setup.py install


RUN pip3 install otaku_info && pip3 uninstall otaku_info -y

ADD . flask-app
RUN cd flask-app && python3 setup.py install

WORKDIR flask-app
CMD ["/usr/bin/python3", "server.py"]
