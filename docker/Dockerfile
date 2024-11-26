##############################################################
# This Dockerfile contains the additional NVIDIA compilers, 
# libraries, and plugins to enable OpenACC and NVIDIA GPU 
# acceleration of Devito codes.
#
# BUILD: docker build --network=host --file docker/Dockerfile --tag pynvml .
# RUN: docker run --gpus all --rm -it  pynvml
##############################################################
FROM python:3.8

ENV DEBIAN_FRONTEND noninteractive 

ADD . /app/.
RUN cd /app && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir . && \
    rm -rf ~/.cache/pip

ADD docker/entrypoint.sh /docker-entrypoint.sh

RUN chmod +x /docker-entrypoint.sh 

## Create App user 
# Set the home directory to our app user's home.
ENV HOME=/app
ENV APP_HOME=/app

WORKDIR /app

EXPOSE 8888
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["bash"]
