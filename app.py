from pathlib import Path
import io
import os
import sqlite3

from flask import Flask, jsonify, render_template, request, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder="stemplates")
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024
VIDEO_FOLDER = Path(app.root_path) / "static" / "videos"
DATABASE_PATH = Path(app.root_path) / "media.db"
ALLOWED_VIDEO_EXTENSIONS = {"mp4", "webm", "mov", "ogg"}
ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}


def is_allowed_video(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS
    )


def get_db():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_db() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                content_type TEXT NOT NULL,
                media_type TEXT NOT NULL CHECK (media_type IN ('image', 'video')),
                data BLOB NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        for path in VIDEO_FOLDER.glob("*"):
            if path.is_file() and is_allowed_video(path.name):
                exists = connection.execute(
                    "SELECT 1 FROM media WHERE filename = ? LIMIT 1",
                    (path.name,),
                ).fetchone()
                if exists is None:
                    connection.execute(
                        """
                        INSERT INTO media (filename, content_type, media_type, data)
                        VALUES (?, ?, 'video', ?)
                        """,
                        (path.name, get_video_content_type(path.name), path.read_bytes()),
                    )


def get_video_content_type(filename):
    extension = filename.rsplit(".", 1)[1].lower()
    return {
        "mp4": "video/mp4",
        "webm": "video/webm",
        "mov": "video/quicktime",
        "ogg": "video/ogg",
    }[extension]


initialize_database()


@app.get("/")
def birthday_home():
    return render_template("trang-chu-sinh-nhat.html")


@app.get("/loi-chuc")
def birthday_wishes():
    return render_template("trang-nhung-cau-chuc.html")


@app.get("/video")
def birthday_video():
    with get_db() as connection:
        videos = connection.execute(
            """
            SELECT id, filename
            FROM media
            WHERE media_type = 'video'
            ORDER BY created_at DESC, id DESC
            """
        ).fetchall()
    return render_template("trang-video-chuc-sinh-nhat.html", videos=videos)


@app.post("/video/upload")
def upload_birthday_video():
    video = request.files.get("video")
    if video is None or not video.filename:
        return jsonify(error="Vui lòng chọn một video."), 400
    if not is_allowed_video(video.filename):
        return jsonify(error="Chỉ hỗ trợ video MP4, WebM, MOV hoặc OGG."), 400

    safe_name = secure_filename(video.filename)
    if not safe_name:
        return jsonify(error="Tên video không hợp lệ."), 400
    content = video.read()
    with get_db() as connection:
        cursor = connection.execute(
            """
            INSERT INTO media (filename, content_type, media_type, data)
            VALUES (?, ?, 'video', ?)
            """,
            (safe_name, get_video_content_type(safe_name), content),
        )
        media_id = cursor.lastrowid
    return jsonify(message="Đã tải video lên thành công.", filename=safe_name, url=f"/media/{media_id}")


@app.post("/media/upload")
def upload_media():
    media = request.files.get("media")
    if media is None or not media.filename:
        return jsonify(error="Vui lòng chọn một hình ảnh hoặc video."), 400

    safe_name = secure_filename(media.filename)
    if not safe_name:
        return jsonify(error="Tên tệp không hợp lệ."), 400

    extension = safe_name.rsplit(".", 1)[-1].lower() if "." in safe_name else ""
    if extension in ALLOWED_VIDEO_EXTENSIONS:
        media_type = "video"
    elif extension in ALLOWED_IMAGE_EXTENSIONS:
        media_type = "image"
    else:
        return jsonify(error="Định dạng hình ảnh hoặc video chưa được hỗ trợ."), 400

    content_type = media.mimetype or "application/octet-stream"
    with get_db() as connection:
        cursor = connection.execute(
            """
            INSERT INTO media (filename, content_type, media_type, data)
            VALUES (?, ?, ?, ?)
            """,
            (safe_name, content_type, media_type, media.read()),
        )
        media_id = cursor.lastrowid
    return jsonify(message="Đã lưu tệp thành công.", filename=safe_name, media_type=media_type, url=f"/media/{media_id}")


@app.get("/media/<int:media_id>")
def serve_media(media_id):
    with get_db() as connection:
        media = connection.execute(
            "SELECT data, content_type, filename FROM media WHERE id = ?",
            (media_id,),
        ).fetchone()
    if media is None:
        return jsonify(error="Không tìm thấy tệp."), 404
    return send_file(
        io.BytesIO(media["data"]),
        mimetype=media["content_type"],
        download_name=media["filename"],
        conditional=True,
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "5000")),
        debug=os.environ.get("FLASK_DEBUG", "").lower() == "true",
    )