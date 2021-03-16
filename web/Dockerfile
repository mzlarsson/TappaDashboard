FROM alpine:3.12

RUN apk add --update --no-cache python3 python3-dev g++ gcc \
    && python3 -m ensurepip --upgrade \
    && pip3 install -U pip \
    && pip3 install flask \
    && apk del --purge python3-dev g++ gcc

ENV FLASK_APP main.py
	
ENTRYPOINT ["python3", "/app/main.py"]