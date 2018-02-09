FROM python:alpine

ADD requirements.txt /
RUN pip install -r /requirements.txt

ADD src/proxy /proxy

EXPOSE 80
ENV PORT=80

COPY run.sh /bin/
ENTRYPOINT [ "run.sh" ]
