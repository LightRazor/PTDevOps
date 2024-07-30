FROM python:3.10-bookworm
WORKDIR /code
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
CMD [ "python", "./Bot1.py"]