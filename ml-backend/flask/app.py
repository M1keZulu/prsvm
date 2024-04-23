from flask import Flask, request, jsonify
import redis
from rq import Queue
import time
from rq.job import Job
import os
from tasks import process_video
from flask_socketio import SocketIO, send, emit
from flask_cors import CORS



app = Flask(__name__)
socket = SocketIO(app)
CORS(app)
socket.init_app(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

r = redis.Redis()
q = Queue(connection=r)

@app.route("/", methods=["GET"])
def hello():
    socket.emit("message", {"data": "Hello World"})
    return jsonify({"message": "Hello World"})

@app.route("/upload_videos", methods=["POST"])
def upload_videos():
    if request.method == "POST":
        files = request.files.getlist("files")
        for file in files:
            filename = file.filename
            if not os.path.exists("database/"+filename):
                os.makedirs("database/"+filename)
            file.save(os.path.join("database/"+filename, filename))
            job = q.enqueue(process_video, filename, time.time(), job_timeout=-1)
        return jsonify({"message": "success"})

if __name__ == "__main__":
    socket.run(app, host= '0.0.0.0', port=443, debug=True)