import cv2
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import logging

capture = None
clients = {}

logging.basicConfig(
    format="[%(asctime)s] %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class CamHandler(BaseHTTPRequestHandler):
        
    def do_GET(self):
        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header(
                'Content-type',
                'multipart/x-mixed-replace; boundary=--jpgboundary'
            )
            self.end_headers()
            clients[self.client_address[0]] = 0
            while True:
                try:

                    rc, img = capture.read()
                    if not rc:
                        continue

                    bimg = cv2.imencode('.jpg', img)[1].tobytes()

                    self.send_header('Content-type', 'image/jpeg')
                    self.send_header('Content-length', len(bimg))
                    self.end_headers()

                    self.wfile.write(bimg)
                    self.wfile.write(b"\r\n--jpgboundary\r\n")
                    clients[self.client_address[0]] += 1
                    if clients[self.client_address[0]] % 1000 == 0:
                        logger.info(f"Sent {clients[self.client_address[0]]} frames to {self.client_address[0]}")
                        
                except KeyboardInterrupt:
                    self.wfile.write(b"\r\n--jpgboundary--\r\n")
                    break
                except BrokenPipeError:
                    continue
            return

        if self.path.endswith('.html'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><head></head><body>')
            self.wfile.write(b'<img src="http://192.168.0.110:8081/cam.mjpg"/>')
            self.wfile.write(b'</body></html>')
            return


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


def main():

    global capture
    capture = cv2.VideoCapture(0)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    global img
    try:
        server = ThreadedHTTPServer(('0.0.0.0', 8081), CamHandler)
        logger.info("Server started at http://127.0.0.1:8081/cam.html")
        server.serve_forever()
    except KeyboardInterrupt:
        capture.release()
        server.socket.close()

if __name__ == '__main__':
    main()
