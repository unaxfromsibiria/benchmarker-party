FROM    python:3.10-slim-buster

RUN     mkdir /opt/app
WORKDIR /opt/app
RUN     apt-get update
RUN     apt-get install -y python3-pip
RUN     apt-get install -y gcc libtiff5-dev libjpeg-dev zlib1g-dev tk
RUN     python -m pip install -U pip
COPY    data data
COPY    requirements.txt requirements.txt
RUN     python -m pip install -r requirements.txt && python -m pip install 'numba<0.57'
COPY    bg_replacer bg_replacer
RUN     cd /opt/app/bg_replacer/cffi_impl/ && python setup.py
RUN     cd /opt/app/bg_replacer/cython_impl/ && python setup.py build_ext --inplace
COPY    Makefile Makefile

CMD ["make", "benchmark_all", "count=50"]
