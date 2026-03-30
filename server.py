from flask import Flask, request, jsonify, render_template
import yt_dlp
from waitress import serve
import os

app = Flask(__name__)
SECRET_KEY = "giadinh123"

@app.route("/")
def home():
    # Hiển thị giao diện App
    return render_template("index.html")

@app.route("/api/download")
def get_video():
    key = request.args.get("key")
    if key != SECRET_KEY:
        return jsonify({"error": "Sai mật khẩu!"}), 403

    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Vui lòng nhập link video"}), 400

    # Cấu hình yt-dlp tối ưu cho cả YouTube và TikTok
    ydl_opts = {
        'format': 'best', 
        'quiet': True,
        'noplaylist': True,
        'no_warnings': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            download_url = info.get("url")
            if not download_url and "entries" in info:
                download_url = info["entries"][0].get("url")

            if not download_url:
                return jsonify({"error": "Không thể lấy link tải trực tiếp."}), 500

            return jsonify({
                "title": info.get("title", "Video"),
                "download_url": download_url
            })
    except Exception as e:
        return jsonify({"error": "Lỗi xử lý link. Hãy kiểm tra lại."}), 500

if __name__ == "__main__":
    # Lấy Port do Render cấp, nếu chạy ở máy tính thì mặc định là 5000
    port = int(os.environ.get("PORT", 5000)) 
    print(f"🚀 App đang chạy tại: http://0.0.0.0:{port}")
    serve(app, host='0.0.0.0', port=port)