# Part 1 : compile C++ code


FROM public.ecr.aws/ubuntu/ubuntu:20.04_stable AS core_builder

# Install packages
RUN apt-get update && \
	apt-get install -y make wget python3 python3-dev gcc g++ g++-8 libstdc++6 clang-7 libyaml-cpp-dev libboost-python1.71-dev libboost-system1.71-dev libboost-filesystem1.71-dev libboost-test1.71-dev && \
	apt-get clean

RUN rm -f /usr/bin/g++ && ln -s /usr/bin/g++-8 /usr/bin/g++ && ln -s /usr/bin/clang++-7 /usr/bin/clang++

# Compile hippocrate
COPY cpp /src

RUN cd /src && ./configure.sh && make clean release
WORKDIR /src



# Part 2 : running Django


FROM public.ecr.aws/ubuntu/ubuntu:20.04_stable

RUN apt-get update && \
	apt-get install -y libpq-dev gcc libboost-python1.71-dev libboost-system1.71-dev python3-pip python3-numpy libjpeg8-dev libyaml-cpp-dev git vim && \
	apt-get clean

RUN mkdir /dependencies
COPY requirements.txt /dependencies

RUN cd /dependencies && pip3 install -r requirements.txt

RUN mkdir /cpp /cpp/hippocrate_cpp && touch /cpp/__init__.py
COPY --from=core_builder /src/hippocrate/*  /cpp/hippocrate_cpp/
ENV PYTHONPATH /cpp
ENV PYTHONUNBUFFERED 1

RUN mkdir /app /django-static /logs
WORKDIR /app

COPY django /app
RUN python3 manage.py collectstatic --noinput

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["/bin/bash", "/app/docker-runserver.sh"]

