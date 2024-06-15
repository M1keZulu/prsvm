from flask import Flask, request, jsonify, send_file
import redis
from rq import Queue
import time
from rq.job import Job
import os
from tasks import process_video, generate_reid_video
from flask_socketio import SocketIO, send, emit
from flask_cors import CORS
import uuid
import secrets
import json


app = Flask(__name__)
socket = SocketIO(app, message_queue='redis://')

app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 * 1024  # 1GB limit

CORS(app)
socket.init_app(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

r = redis.Redis()
q = Queue(connection=r, default_timeout='3h')

@app.route("/", methods=["GET"])
def hello():
    socket.emit("message", {"data": "Hello World"})
    return jsonify({"message": "Hello World"})

#socket io complete event
@socket.on("complete")
def complete(data):
    print(data)
    socket.emit("complete", data)

@app.route("/delete_video", methods=["DELETE"])
def delete_video():
    video_name = request.json["video_name"]
    if os.path.exists("database/"+video_name):
        if os.path.exists("database/"+video_name+"/"+"video."+video_name.split(".")[-1]):
            os.remove("database/"+video_name+"/"+"video."+video_name.split(".")[-1])
        if os.path.exists("database/"+video_name+"/"+"detections.json"):
            os.remove("database/"+video_name+"/"+"detections.json")
        #remove all files in directory
        for file in os.listdir("database/"+video_name):
            os.remove("database/"+video_name+"/"+file)
        
        os.rmdir("database/"+video_name)
        return jsonify({"message": "Video deleted successfully."})
    else:
        return jsonify({"error": "Video not found."}), 404

@app.route("/process_video", methods=["POST"])
def process_video_route():
    video_name = request.json["video_name"]
    video_path = "database/"+video_name+"/"+"video."+video_name.split(".")[-1]
    if os.path.exists("database/"+video_name+"/"+"detections.json"):
        return jsonify({"error": "Video already processed."}), 400
    if video_name in q.job_ids:
        return jsonify({"error": "Video already in queue."}), 400
    if not os.path.exists(video_path):
        return jsonify({"error": "Video not found."}), 404
    job = q.enqueue(process_video, video_name, video_name, job_id=video_name, result_ttl=-1)
    with open("database/"+video_name+"/"+"detections.json", "w") as f:
        pass
    return jsonify({"success": "Video added to queue.", "job_id": job.id})

@app.route("/job_position/<job_id>", methods=["GET"])
def job_position(job_id):
    try:
        job = Job.fetch(job_id, connection=r)
        return jsonify({"status": job.get_status(), "position": q.get_job_position(job_id)})
    except:
        return jsonify({"error": "Job not found."}), 404
    

@app.route("/upload_video", methods=["POST"])
def upload_video():
    print(request.files)
    if "file" not in request.files:
        return jsonify({"error": "No video file received."}), 400

    video_file = request.files["file"]
    if not video_file.filename or not video_file.filename.endswith(".mp4"):
        return jsonify({"error": "Invalid file format."}), 400

    if not os.path.exists("database/"+video_file.filename):
        os.makedirs("database/"+video_file.filename)
    print(video_file.filename)
    video_file.save(os.path.join("database/"+video_file.filename, "video."+video_file.filename.split(".")[-1]))
    #enqeue and return job id
    user_token = secrets.token_urlsafe(128)
    video_tokens[user_token] = "database/"+video_file.filename+"/"+"video."+video_file.filename.split(".")[-1]
    #dump video tokens to file
    with open("video_tokens.json", "w") as f:
        json.dump(video_tokens, f)
    return jsonify({"job_id": video_file.filename, "secure_url": f'/playback?token={user_token}'})
                    
@app.route("/job_status/<job_id>", methods=["GET"])
def job_status(job_id):
    job = Job.fetch(job_id, connection=r)
    return jsonify({"status": job.get_status()}), 200

@app.route('/playback')
def play_video():
    user_token = request.args.get('token')
    if user_token in video_tokens:
        video_path = video_tokens[user_token]
        return send_file(video_path, mimetype='video/mp4')
    else:
        return 'Invalid token', 403 
    
@app.route('/query_image/<filename>')
def get_image(filename):
    return send_file("database/incidents/"+filename, mimetype='image/jpg')

@app.route("/gallery", methods=["GET"])
def get_gallery():
    return send_file(request.args.get("image"), mimetype='image/jpg')

    
@app.route("/query_reid", methods=["POST"])
def get_detections():
    print(request.json)
    video_name = request.json["video_name"]
    timestamp = request.json["timestamp"]
    height = request.json["height"]
    width = request.json["width"]
    x = request.json["x"]
    y = request.json["y"]
    filenames = request.json["filenames"]

    job_id = str(uuid.uuid4())
    video_tokens[job_id] = "database/incidents/"+job_id+".mp4"
    with open("video_tokens.json", "w") as f:
        json.dump(video_tokens, f)
    job = q.enqueue(generate_reid_video, filenames, video_name, timestamp, height, width, x, y, job_id, job_id=job_id, result_ttl=-1)
    return jsonify({"job_id": job.id, "secure_url": f"/playback?token={job_id}", "query_url": f"/query_image/{job_id}.jpg"})

@app.route("/delete_incident", methods=["POST"])
def delete_incident():
    print(request.json)
    id = request.json["id"]
    if os.path.exists("database/incidents/"+id+".mp4"):
        os.remove("database/incidents/"+id+".mp4")
    if os.path.exists("database/incidents/"+id+".jpg"):
        os.remove("database/incidents/"+id+".jpg")
    return jsonify({"message": "Incident deleted successfully."})

if __name__ == "__main__":
    video_tokens = {}
    if os.path.exists("video_tokens.json"):
        with open("video_tokens.json", "r") as f:
            video_tokens = json.load(f)
    socket.run(app, host= '0.0.0.0', port=8000, debug=True)
    