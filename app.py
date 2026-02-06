"""
Alla Kan AI - TikTok Integration Demo
Deployed on Render.com
"""

from flask import Flask, redirect, request, render_template_string, session, url_for
import httpx
import secrets
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(16))

# =============================================================================
# TikTok Credentials from environment variables
# =============================================================================
TIKTOK_CLIENT_KEY = os.environ.get("TIKTOK_CLIENT_KEY", "awkdujek122kz1rf")
TIKTOK_CLIENT_SECRET = os.environ.get("TIKTOK_CLIENT_SECRET", "bWHmtjj6QxrJYfyw07rOqyGfjCbBddjD")
REDIRECT_URI = os.environ.get("REDIRECT_URI", "https://allakanai-demo.onrender.com/callback")
# TikTok API endpoints
TIKTOK_AUTH_URL = "https://www.tiktok.com/v2/auth/authorize/"
TIKTOK_TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
TIKTOK_USER_URL = "https://open.tiktokapis.com/v2/user/info/"

# =============================================================================
# HTML Templates
# =============================================================================

HOME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Alla Kan AI - TikTok Integration</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            padding: 60px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
            max-width: 500px;
        }
        .logo { font-size: 48px; margin-bottom: 10px; }
        h1 { color: #1a1a1a; margin-bottom: 10px; font-size: 28px; }
        .subtitle { color: #666; margin-bottom: 40px; font-size: 16px; }
        .login-btn {
            background: #000;
            color: white;
            padding: 16px 40px;
            border: none;
            border-radius: 30px;
            font-size: 18px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 12px;
            text-decoration: none;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .login-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .features { margin-top: 40px; text-align: left; }
        .feature {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 0;
            border-bottom: 1px solid #eee;
        }
        .feature:last-child { border-bottom: none; }
        .check { color: #22c55e; font-size: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🤖</div>
        <h1>Alla Kan AI</h1>
        <p class="subtitle">Educational AI Content for Swedish Audiences</p>
        <a href="/login" class="login-btn">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
                <path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64 2.93 2.93 0 0 1 .88.13V9.4a6.84 6.84 0 0 0-1-.05A6.33 6.33 0 0 0 5 20.1a6.34 6.34 0 0 0 10.86-4.43v-7a8.16 8.16 0 0 0 4.77 1.52v-3.4a4.85 4.85 0 0 1-1-.1z"/>
            </svg>
            Login with TikTok
        </a>
        <div class="features">
            <div class="feature"><span class="check">✓</span><span>Secure OAuth 2.0 Authentication</span></div>
            <div class="feature"><span class="check">✓</span><span>Automated Video Posting</span></div>
            <div class="feature"><span class="check">✓</span><span>Scheduled Content Publishing</span></div>
        </div>
    </div>
</body>
</html>
"""

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Alla Kan AI - Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; }
        .header {
            background: #1e293b;
            padding: 20px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #334155;
        }
        .header h1 { font-size: 24px; }
        .header h1 span { color: #60a5fa; }
        .user-info {
            display: flex;
            align-items: center;
            gap: 12px;
            background: #334155;
            padding: 8px 16px;
            border-radius: 30px;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 40px; }
        .success-banner {
            background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
            padding: 20px 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 24px;
        }
        .card {
            background: #1e293b;
            border-radius: 16px;
            padding: 30px;
            border: 1px solid #334155;
        }
        .card h2 {
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #94a3b8;
            margin-bottom: 20px;
        }
        .video-item {
            background: #0f172a;
            padding: 16px;
            border-radius: 10px;
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .status-ready { background: #22c55e20; color: #22c55e; padding: 6px 12px; border-radius: 20px; font-size: 12px; }
        .status-scheduled { background: #60a5fa20; color: #60a5fa; padding: 6px 12px; border-radius: 20px; font-size: 12px; }
        .post-btn {
            background: linear-gradient(135deg, #ff0050 0%, #00f2ea 100%);
            color: white;
            padding: 14px 28px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            margin-top: 20px;
        }
        .schedule-item {
            display: flex;
            justify-content: space-between;
            padding: 12px;
            background: #0f172a;
            border-radius: 8px;
            margin-bottom: 12px;
        }
        .time { color: #60a5fa; font-weight: 600; }
        .logout-btn { color: #94a3b8; text-decoration: none; font-size: 14px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Alla Kan <span>A.I.</span></h1>
        <div class="user-info">
            <span>👤 {{ username }}</span>
            <a href="/logout" class="logout-btn">Logout</a>
        </div>
    </div>
    <div class="container">
        <div class="success-banner">
            <span style="font-size:32px">✅</span>
            <div>
                <strong>TikTok Connected Successfully!</strong>
                <p style="opacity:0.9;margin-top:4px">Your account is now linked. You can post videos automatically.</p>
            </div>
        </div>
        <div class="grid">
            <div class="card">
                <h2>📹 Video Queue</h2>
                <div class="video-item">
                    <span>A.I. förstår svenska bättre än du tror</span>
                    <span class="status-ready">Ready</span>
                </div>
                <div class="video-item">
                    <span>Så hjälper A.I. läkare hitta cancer</span>
                    <span class="status-ready">Ready</span>
                </div>
                <div class="video-item">
                    <span>Din telefon är smartare än du tror</span>
                    <span class="status-scheduled">Scheduled</span>
                </div>
                <button class="post-btn" onclick="simulatePost()">🚀 Post Next Video to TikTok</button>
            </div>
            <div class="card">
                <h2>📅 Today's Schedule</h2>
                <div class="schedule-item">
                    <span class="time">08:00</span>
                    <span>Morning Post</span>
                    <span style="color:#22c55e">✓ Posted</span>
                </div>
                <div class="schedule-item">
                    <span class="time">13:00</span>
                    <span>Lunch Post</span>
                    <span style="color:#f59e0b">⏳ Pending</span>
                </div>
                <div class="schedule-item">
                    <span class="time">19:00</span>
                    <span>Evening Post</span>
                    <span style="color:#94a3b8">— Scheduled</span>
                </div>
            </div>
            <div class="card">
                <h2>📊 This Week</h2>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
                    <div style="background:#0f172a;padding:20px;border-radius:10px;text-align:center">
                        <div style="font-size:32px;font-weight:700">12</div>
                        <div style="color:#94a3b8;font-size:14px">Videos Posted</div>
                    </div>
                    <div style="background:#0f172a;padding:20px;border-radius:10px;text-align:center">
                        <div style="font-size:32px;font-weight:700;color:#22c55e">24.5K</div>
                        <div style="color:#94a3b8;font-size:14px">Total Views</div>
                    </div>
                </div>
            </div>
            <div class="card">
                <h2>⚙️ Integration Status</h2>
                <div class="video-item"><span>TikTok Login Kit</span><span style="color:#22c55e">✓ Connected</span></div>
                <div class="video-item"><span>Content Posting API</span><span style="color:#22c55e">✓ Active</span></div>
                <div class="video-item"><span>Token Status</span><span style="color:#22c55e">✓ Valid</span></div>
            </div>
        </div>
    </div>
    <script>
        function simulatePost() {
            alert('Video posting initiated!\\n\\nAPI Call: POST /v2/post/publish/video/init/\\nStatus: Uploading to TikTok...\\n\\nThis demonstrates the Content Posting API integration.');
        }
    </script>
</body>
</html>
"""

ERROR_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Error - Alla Kan AI</title>
    <style>
        body { font-family: -apple-system, sans-serif; background: #0f172a; color: white; display: flex; align-items: center; justify-content: center; min-height: 100vh; }
        .error-box { background: #1e293b; padding: 40px; border-radius: 16px; text-align: center; max-width: 500px; }
        h1 { color: #ef4444; margin-bottom: 10px; }
        p { color: #94a3b8; margin-bottom: 20px; }
        a { color: #60a5fa; }
        .error-details { background: #0f172a; padding: 15px; border-radius: 8px; font-family: monospace; font-size: 12px; text-align: left; margin-top: 20px; word-break: break-all; }
    </style>
</head>
<body>
    <div class="error-box">
        <div style="font-size:48px;margin-bottom:20px">⚠️</div>
        <h1>{{ error_title }}</h1>
        <p>{{ error_message }}</p>
        <a href="/">← Back to Home</a>
        {% if error_details %}<div class="error-details">{{ error_details }}</div>{% endif %}
    </div>
</body>
</html>
"""

# =============================================================================
# Routes
# =============================================================================

@app.route("/")
def home():
    if session.get("tiktok_user"):
        return redirect("/dashboard")
    return render_template_string(HOME_TEMPLATE)

@app.route("/login")
def login():
    state = secrets.token_urlsafe(16)
    session["oauth_state"] = state
    scopes = "user.info.basic,video.publish,video.upload"
    auth_url = (
        f"{TIKTOK_AUTH_URL}"
        f"?client_key={TIKTOK_CLIENT_KEY}"
        f"&response_type=code"
        f"&scope={scopes}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&state={state}"
    )
    return redirect(auth_url)

@app.route("/callback")
def callback():
    error = request.args.get("error")
    if error:
        return render_template_string(ERROR_TEMPLATE,
            error_title="Authorization Failed",
            error_message=request.args.get("error_description", "Unknown error"),
            error_details=error)

    code = request.args.get("code")
    state = request.args.get("state")

    if state != session.get("oauth_state"):
        return render_template_string(ERROR_TEMPLATE,
            error_title="Security Error",
            error_message="State mismatch",
            error_details=None)

    if not code:
        return render_template_string(ERROR_TEMPLATE,
            error_title="No Code",
            error_message="No authorization code received",
            error_details=None)

    try:
        with httpx.Client() as client:
            response = client.post(TIKTOK_TOKEN_URL, data={
                "client_key": TIKTOK_CLIENT_KEY,
                "client_secret": TIKTOK_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": REDIRECT_URI,
            })
            token_data = response.json()

        if "access_token" not in token_data:
            return render_template_string(ERROR_TEMPLATE,
                error_title="Token Error",
                error_message="Failed to get access token",
                error_details=str(token_data))

        session["access_token"] = token_data["access_token"]

        with httpx.Client() as client:
            user_response = client.get(TIKTOK_USER_URL,
                headers={"Authorization": f"Bearer {token_data['access_token']}"},
                params={"fields": "open_id,display_name,avatar_url"})
            user_data = user_response.json()

        session["tiktok_user"] = user_data.get("data", {}).get("user", {})
        return redirect("/dashboard")

    except Exception as e:
        return render_template_string(ERROR_TEMPLATE,
            error_title="Connection Error",
            error_message=str(e),
            error_details=None)

@app.route("/dashboard")
def dashboard():
    user = session.get("tiktok_user", {})
    username = user.get("display_name", "TikTok User")
    return render_template_string(DASHBOARD_TEMPLATE, username=username)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
@app.route("/tiktokjJA0uDugeqcgJjXGt7AtL0tUUkOTTDpK.txt")
  def tiktok_verify():
      return "tiktokjJA0uDugeqcgJjXGt7AtL0tUUkOTTDpK", 200, {"Content-Type": "text/plain"}
      
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

