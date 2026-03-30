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
        'format': 'b[ext=mp4]/b/best',
        'quiet': True,
        'noplaylist': True,
        'no_warnings': True,
        'extractor_args': {'youtube': ['client=android,ios,tv']}, # Cứ giữ lại dòng hôm trước cho chắc ăn
        'cookiefile': 'cookies.txt'  # 🔥 THÊM DÒNG NÀY: Báo cho yt-dlp biết chỗ lấy thẻ căn cước
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            download_url = info.get("url")
            
            # 🔥 BƯỚC LỌC THÔNG MINH: Ngăn chặn lỗi bốc nhầm file ảnh (.jpg, .webp, storyboard)
            if download_url and (".jpg" in download_url or "storyboard" in download_url):
                download_url = None # Hủy link ảnh lỗi
                
                # Tự tay lục lọi trong danh sách các định dạng của YouTube để tìm file MP4 chuẩn
                if "formats" in info:
                    # Lặp ngược từ dưới lên (vì yt-dlp thường để file xịn nhất ở cuối)
                    for f in reversed(info["formats"]):
                        # Điều kiện: Có video (vcodec), có âm thanh (acodec) và là đuôi mp4
                        if f.get("vcodec") != "none" and f.get("acodec") != "none" and f.get("ext") == "mp4":
                            download_url = f.get("url")
                            break # Tìm thấy là dừng luôn

            # Xử lý fallback cho các trang khác (TikTok)
            if not download_url and "entries" in info:
                download_url = info["entries"][0].get("url")

            if not download_url:
                return jsonify({"error": "Không thể lấy link video chuẩn. Vui lòng thử lại!"}), 500

            return jsonify({
                "title": info.get("title", "Video"),
                "download_url": download_url
            })

    except Exception as e:
        return jsonify({"error": f"Lỗi từ hệ thống: {str(e)}"}), 500

if __name__ == "__main__":
    # Lấy Port do Render cấp, nếu chạy ở máy tính thì mặc định là 5000
    port = int(os.environ.get("PORT", 5000)) 
    print(f"🚀 App đang chạy tại: http://0.0.0.0:{port}")
    serve(app, host='0.0.0.0', port=port)