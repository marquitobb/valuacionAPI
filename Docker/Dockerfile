FROM python:3
ADD src/ /src
WORKDIR /src
RUN apt-get update
RUN pip install -r requirements.txt
CMD python app.py