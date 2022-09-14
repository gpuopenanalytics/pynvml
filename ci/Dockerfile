# syntax=docker/dockerfile:1.2
# pynvml as distributed on pypi requires python 3.6+
# This Dockerfile builds and tests for python 2.7
#
# Supports Ubuntu 16.04 and 20.04

#### Build Stage
################################################################################
ARG UBUNTU_BASE_TAG=16.04
FROM ubuntu:${UBUNTU_BASE_TAG} as pynvml-build
LABEL description="Build image for pynvml"

ARG DEBIAN_FRONTEND=noninteractive

SHELL ["/bin/bash", "-c"]

RUN apt-get update \
    && apt-get install -y \
        curl \
        git \
        python \
    && apt-get clean

# pip and virtualenv (available as package on 16.04 but not 20.04)
RUN curl https://bootstrap.pypa.io/pip/2.7/get-pip.py | python2 \
     && python2 -m pip --no-cache-dir install virtualenv

ADD . /sandbox
WORKDIR /sandbox

RUN virtualenv env \
    && source env/bin/activate \
    && pip install --no-cache-dir . \
    && pip install --upgrade --no-cache-dir pytest future wheel setuptools

CMD nvidia-smi && source env/bin/activate \
    && pytest -rxXspF pynvml/tests \
    && python setup.py bdist_wheel --dist-dir /sandbox/dist
