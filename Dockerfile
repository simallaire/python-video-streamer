FROM spallaire93/opencv-python 


COPY main.py /app/main.py

WORKDIR /app
ENTRYPOINT [ "python", "main.py" ]
