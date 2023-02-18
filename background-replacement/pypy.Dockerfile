FROM    pypy:3.9-slim-bullseye

RUN     mkdir /opt/app
WORKDIR /opt/app
RUN     apt-get update
RUN     apt-get install -y libtiff5-dev libjpeg-dev zlib1g-dev build-essential tk
RUN     python --version && python -m pip install -U pip
COPY    data data
COPY    requirements.txt requirements.txt
RUN     python -m pip install -r requirements.txt
COPY    bg_replacer bg_replacer
COPY    Makefile Makefile

CMD ["make", "benchmark_pypy", "count=50"]
