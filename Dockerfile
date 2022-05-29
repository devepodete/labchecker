FROM ubuntu:18.04

RUN mkdir /home/checker-home
WORKDIR /home/checker-home

RUN apt-get update && apt-get install -y python3 python3-pip gcc g++ make cmake git
RUN git clone https://github.com/devepodete/labchecker
RUN git clone https://github.com/devepodete/taskgenerator

WORKDIR /home/checker-home/labchecker
RUN pip3 install -r requirements.txt
