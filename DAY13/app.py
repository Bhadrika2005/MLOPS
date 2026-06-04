"""
ATM CCTV Surveillance Intelligence System — Flask Backend
"""

import os, sys, uuid, threading, json, time
from pathlib import Path
from datetime import datetime
from dataclasses import asdict

from flask import (Flask, render_template, request, jsonify,
                   send_from_directory, abort, url_for)


BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH  = os.path.join(BASE_DIR, "best.pt")
UPLOAD_DIR  = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR  = os.path.join(BASE_DIR, "output")
CLIPS_DIR   = os.path.join(OUTPUT_DIR, "clips")
PROC_DIR    = os.path.join(OUTPUT_DIR, "processed")
REPORTS_DIR = os.path.join(OUTPUT_DIR, "reports")

for d in [UPLOAD_DIR, CLIPS_DIR, PROC_DIR, REPORTS_DIR]:
    os.makedirs(d, exist_ok=True)

sys.path.insert(0, BASE_DIR)
from analyzer import ATMAnalyzer
from report_generator import generate_csv_report, generate_pdf_report

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024 * 1024  # 2 GB

ALLOWED_EXT = {".mp4", ".avi", ".mov"}


jobs: dict[str, dict] = {}
jobs_lock = threading.Lock()


def _fmt_ts(sec: float) -> str:
    sec = float(sec or 0)
    h, rem = divmod(int(sec), 3600)
    m, s   = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def incident_to_dict(inc) -> dict:
    return {
        "type":        inc.incident_type,
        "timestamp":   _fmt_ts(inc.timestamp_sec),
        "ts_sec":      inc.timestamp_sec,
        "severity":    inc.severity,
        "description": inc.description,
        "track_ids":   inc.track_ids,
        "clip_path":   inc.clip_path,
        "clip_name":   os.path.basename(inc.clip_path) if inc.clip_path else "",
        "clip_exists": bool(inc.clip_path and os.path.exists(inc.clip_path)),
    }


def result_to_dict(r: dict) -> dict:
    incidents = [incident_to_dict(i) for i in r.get("incidents", [])]
    return {
        "video_name":    r.get("original_name", r.get("video_name", "")),
        "duration":      _fmt_ts(r.get("duration_sec", 0)),
        "duration_sec":  r.get("duration_sec", 0),
        "fps":           round(r.get("fps", 0), 2),
        "total_frames":  r.get("total_frames", 0),
        "total_visitors":r.get("total_visitors", 0),
        "incidents":     incidents,
        "incident_count":len(incidents),
        "high_count":    sum(1 for i in incidents if i["severity"] == "HIGH"),
        "medium_count":  sum(1 for i in incidents if i["severity"] == "MEDIUM"),
        "processed_name":os.path.basename(r.get("processed_path", "")),
        "processed_exists": bool(r.get("processed_path") and os.path.exists(r["processed_path"])),
    }



def _run_analysis(job_id: str, video_paths: list[str],
                  original_names: list[str], thresholds: dict):
    import analyzer as _ana
    _ana.LOITER_THRESHOLD_SEC       = thresholds.get("loiter",  15)
    _ana.CROWD_THRESHOLD            = thresholds.get("crowd",   3)
    _ana.TAMPER_STILL_THRESHOLD_SEC = thresholds.get("tamper",  8)
    _ana.REENTRY_THRESHOLD          = thresholds.get("reentry", 2)

    try:
        analyzer = ATMAnalyzer(MODEL_PATH, OUTPUT_DIR)
    except Exception as e:
        with jobs_lock:
            jobs[job_id]["status"]  = "error"
            jobs[job_id]["message"] = f"Model load failed: {e}"
        return

    results = []
    for idx, (vpath, vname) in enumerate(zip(video_paths, original_names)):
        with jobs_lock:
            jobs[job_id]["current_file"]  = vname
            jobs[job_id]["file_index"]    = idx + 1
            jobs[job_id]["file_total"]    = len(video_paths)
            jobs[job_id]["status"]        = "running"
            jobs[job_id]["frame_progress"]= 0

        def cb(cur, total, jid=job_id):
            with jobs_lock:
                jobs[jid]["frame_progress"] = int(100 * cur / max(total, 1))

        try:
            result = analyzer.analyze_video(vpath, progress_callback=cb)
            result["original_name"] = vname
            results.append(result_to_dict(result))
        except Exception as e:
            with jobs_lock:
                jobs[job_id]["errors"] = jobs[job_id].get("errors", [])
                jobs[job_id]["errors"].append(f"{vname}: {e}")

    with jobs_lock:
        jobs[job_id]["status"]  = "done"
        jobs[job_id]["results"] = results
        jobs[job_id]["message"] = f"Processed {len(results)} video(s)"




@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/upload", methods=["POST"])
def upload():
    files = request.files.getlist("videos")
    if not files or not files[0].filename:
        return jsonify({"error": "No files uploaded"}), 400

    try:
        loiter  = int(request.form.get("loiter",  15))
        crowd   = int(request.form.get("crowd",   3))
        tamper  = int(request.form.get("tamper",  8))
        reentry = int(request.form.get("reentry", 2))
    except ValueError:
        return jsonify({"error": "Invalid threshold values"}), 400

    saved_paths = []
    original_names = []
    for f in files:
        ext = Path(f.filename).suffix.lower()
        if ext not in ALLOWED_EXT:
            return jsonify({"error": f"Unsupported format: {f.filename}"}), 400
        safe_name = f"{uuid.uuid4().hex}{ext}"
        dest = os.path.join(UPLOAD_DIR, safe_name)
        f.save(dest)
        saved_paths.append(dest)
        original_names.append(f.filename)

    job_id = uuid.uuid4().hex
    with jobs_lock:
        jobs[job_id] = {
            "status": "queued",
            "frame_progress": 0,
            "file_index": 0,
            "file_total": len(saved_paths),
            "current_file": "",
            "message": "Queued",
            "results": [],
            "errors": [],
        }

    t = threading.Thread(
        target=_run_analysis,
        args=(job_id, saved_paths, original_names,
              {"loiter": loiter, "crowd": crowd, "tamper": tamper, "reentry": reentry}),
        daemon=True,
    )
    t.start()

    return jsonify({"job_id": job_id})


@app.route("/api/job/<job_id>")
def job_status(job_id):
    with jobs_lock:
        job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(job)


@app.route("/api/clips")
def list_clips():
    clips = []
    for f in sorted(Path(CLIPS_DIR).glob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True):
        clips.append({
            "name": f.name,
            "size_mb": round(f.stat().st_size / 1e6, 2),
            "mtime": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
        })
    return jsonify(clips)


@app.route("/api/report/<fmt>", methods=["POST"])
def export_report(fmt):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400

    # Reconstruct a minimal result dict the report generator expects
    class _Inc:
        pass

    incidents = []
    for d in data.get("incidents", []):
        inc = _Inc()
        inc.incident_type = d["type"]
        inc.timestamp_sec = d["ts_sec"]
        inc.severity      = d["severity"]
        inc.description   = d["description"]
        inc.track_ids     = d["track_ids"]
        inc.clip_path     = d["clip_path"]
        incidents.append(inc)

    result = {
        "video_name":    data.get("video_name", "video"),
        "original_name": data.get("video_name", "video"),
        "duration_sec":  data.get("duration_sec", 0),
        "total_visitors":data.get("total_visitors", 0),
        "incidents":     incidents,
    }

    stem = Path(data.get("video_name", "report")).stem
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")

    if fmt == "csv":
        path = os.path.join(REPORTS_DIR, f"{stem}_{ts}.csv")
        generate_csv_report(result, path)
        return send_from_directory(REPORTS_DIR, os.path.basename(path),
                                   as_attachment=True, mimetype="text/csv")
    elif fmt == "pdf":
        path = os.path.join(REPORTS_DIR, f"{stem}_{ts}.pdf")
        out  = generate_pdf_report(result, path)
        return send_from_directory(REPORTS_DIR, os.path.basename(out),
                                   as_attachment=True, mimetype="application/pdf")
    else:
        return jsonify({"error": "Unknown format"}), 400


@app.route("/output/clips/<filename>")
def serve_clip(filename):
    return send_from_directory(CLIPS_DIR, filename)


@app.route("/output/processed/<filename>")
def serve_processed(filename):
    return send_from_directory(PROC_DIR, filename)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False,
        threaded=True
    )
