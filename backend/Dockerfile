FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv git

WORKDIR /app
COPY requirements.txt .

RUN python3 -m venv venv
RUN . venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

EXPOSE 11156
CMD ["/bin/bash", "-c", ". venv/bin/activate && uvicorn server:app --host 0.0.0.0 --port 11156 --reload"]