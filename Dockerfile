FROM choros

MAINTAINER Georg Grab

COPY data /data
COPY Backgroundpool /Backgroundpool
COPY Servertools /Servertools
COPY bilderStrukturen /bilderStrukturen

RUN /Servertools/Backman/setasbackground.py -i 0x0 use

VOLUME /data
VOLUME /Servertools
VOLUME /bilderStrukturen
