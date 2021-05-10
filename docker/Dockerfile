##############################################################
# This Dockerfile contains the additional NVIDIA compilers, 
# libraries, and plugins to enable OpenACC and NVIDIA GPU 
# acceleration of Devito codes.
#
# BUILD: docker build --network=host --file docker/Dockerfile --tag pynvml .
# RUN: docker run --gpus all --rm -it -p 8888:8888 -p 8787:8787 -p 8786:8786 pynvml
##############################################################
FROM python:3.6

ENV DEBIAN_FRONTEND noninteractive 

ADD ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt && \
    rm -rf ~/.cache/pip

ADD ./pynvml /app/pynvml
ADD ./setup.py /app/
ADD ./setup.cfg /app/
ADD ./README.md /app/
ADD ./PKG-INFO /app/
ADD ./MANIFEST.in /app/
ADD ./help_query_gpu.txt /app/
ADD docker/entrypoint.sh /docker-entrypoint.sh

RUN chmod +x  /docker-entrypoint.sh 

## Create App user 
# Set the home directory to our app user's home.
ENV HOME=/app
ENV APP_HOME=/app

WORKDIR /app

EXPOSE 8888
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["bash"]
