FROM spallaire93/opencv-python 

RUN pip install imutils \
    flask
COPY main.py /app/main.py

WORKDIR /app
ENTRYPOINT [ "python", "main.py" ]