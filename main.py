import cv2
import imutils
from flask import Flask, Response

camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
app = Flask(__name__)

def generate():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Resize the frame for faster processing
            frame = imutils.resize(frame, width=1920)
            # Encode the frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            # Yield the frame in bytes
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
def generate_snapshot():
    success, frame = camera.read()
    if success:
        # Resize the frame for faster processing
        frame = imutils.resize(frame, width=1920)
        # Encode the frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        # Yield the frame in bytes
        return frame
    else:
        return None

    
    
@app.route('/stream')
def video_feed():
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/snapshot')
def snapshot_feed():
    snapshot = generate_snapshot()
    if snapshot:
        return Response(snapshot, mimetype='image/jpeg')
    else:
        return render_template('error.html')

if __name__ == '__main__':
    if camera.isOpened():
        app.run(host='0.0.0.0', port=8000)
