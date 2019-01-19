FROM python:3.7

MAINTAINER Evgeny.Kovalev@skoltech.ru

WORKDIR project

RUN pip install matplotlib wordcloud

ADD oldman.txt ./
ADD oldman_project.py ./

VOLUME /project/results

CMD ["python", "oldman_project.py"]