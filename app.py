"""
  Alla Kan AI - TikTok Integration Demo
  """

  from flask import Flask, redirect, request, render_template_string, session
  import httpx
  import secrets
  import os

  app = Flask(__name__)
  app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(16))

  TIKTOK_CLIENT_KEY = os.environ.get("TIKTOK_CLIENT_KEY", "awkdujek122kz1rf")
  TIKTOK_CLIENT_SECRET = os.environ.get("TIKTOK_CLIENT_SECRET", "bWHmtjj6QxrJYfyw07rOqyGfjCbBddjD")
  REDIRECT_URI = os.environ.get("REDIRECT_URI", "https://allakanai-demo.onrender.com/callback")

  TIKTOK_AUTH_URL = "https://www.tiktok.com/v2/auth/authorize/"
  TIKTOK_TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
  TIKTOK_USER_URL = "https://open.tiktokapis.com/v2/user/info/"

  HOME_TEMPLATE = """
  <!DOCTYPE html>
  <html>
  <head>
      <title>Alla Kan AI - TikTok Integration</title>
      <style>
          * { margin: 0; padding: 0; box-sizing: border-box; }
          body { font-family: -apple-system, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex;
  align-items: center; justify-content: center; }
          .container { background: white; padding: 60px; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); text-align: center; max-width: 500px;
   }
          .logo { font-size: 48px; margin-bottom: 10px; }
          h1 { color: #1a1a1a; margin-bottom: 10px; font-size: 28px; }
          .subtitle { color: #666; margin-bottom: 40px; font-size: 16px; }
          .login-btn { background: #000; color: white; padding: 16px 40px; border: none; border-radius: 30px; font-size: 18px; cursor: pointer; display:
  inline-flex; align-items: center; gap: 12px; text-decoration: none; }
          .features { margin-top: 40px; text-align: left; }
          .feature { display: flex; align-items: center; gap: 12px; padding: 12px 0; border-bottom: 1px solid #eee; }
          .check { color: #22c55e; font-size: 20px; }
      </style>
  </head>
  <body>
      <div class="container">
          <div class="logo"></div>
          <h1>Alla Kan AI</h1>
          <p class="subtitle">Educational AI Content for Swedish Audiences</p>
          <a href="/login" class="login-btn">Login with TikTok</a>
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
          .header { background: #1e293b; padding: 20px 40px; display: flex; justify-content: space-between; align-items: center; }
          .header h1 { font-size: 24px; }
          .header h1 span { color: #60a5fa; }
          .container { max-width: 1200px; margin: 0 auto; padding: 40px; }
          .success-banner { background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); padding: 20px 30px; border-radius: 12px; margin-bottom: 30px; }
          .card { background: #1e293b; border-radius: 16px; padding: 30px; margin-bottom: 20px; }
          .card h2 { font-size: 14px; text-transform: uppercase; color: #94a3b8; margin-bottom: 20px; }
          .video-item { background: #0f172a; padding: 16px; border-radius: 10px; margin-bottom: 12px; display: flex; justify-content: space-between; }
          .post-btn { background: linear-gradient(135deg, #ff0050 0%, #00f2ea 100%); color: white; padding: 14px 28px; border: none; border-radius: 10px;
  font-size: 16px; cursor: pointer; width: 100%; margin-top: 20px; }
      </style>
  </head>
  <body>
      <div class="header">
          <h1>Alla Kan <span>A.I.</span></h1>
          <span>{{ username }}</span>
      </div>
      <div class="container">
          <div class="success-banner">
              <strong>✅ TikTok Connected Successfully!</strong>
              <p>Your account is now linked. You can post videos automatically.</p>
          </div>
          <div class="card">
              <h2>Video Queue</h2>
              <div class="video-item"><span>A.I. förstår svenska bättre än du tror</span><span style="color:#22c55e">Ready</span></div>
              <div class="video-item"><span>Så hjälper A.I. läkare hitta cancer</span><span style="color:#22c55e">Ready</span></div>
              <button class="post-btn" onclick="alert('Video posting initiated via Content Posting API!')">🚀 Post Next Video to TikTok</button>
          </div>
          <div class="card">
              <h2>Integration Status</h2>
              <div class="video-item"><span>TikTok Login Kit</span><span style="color:#22c55e">✓ Connected</span></div>
              <div class="video-item"><span>Content Posting API</span><span style="color:#22c55e">✓ Active</span></div>
          </div>
      </div>
  </body>
  </html>
  """

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
      auth_url = f"{TIKTOK_AUTH_URL}?client_key={TIKTOK_CLIENT_KEY}&response_type=code&scope={scopes}&redirect_uri={REDIRECT_URI}&state={state}"
      return redirect(auth_url)

  @app.route("/callback")
  def callback():
      code = request.args.get("code")
      if not code:
          return "Error: No code received", 400
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
              return f"Error: {token_data}", 400
          session["access_token"] = token_data["access_token"]
          session["tiktok_user"] = {"display_name": "TikTok User"}
          return redirect("/dashboard")
      except Exception as e:
          return f"Error: {e}", 500

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
      return "tiktok-developers-site-verification=jJA0uDugeqcgJjXGt7AtL0tUUkOTTDpK", 200, {"Content-Type": "text/plain"}

  if __name__ == "__main__":
      port = int(os.environ.get("PORT", 5000))
      app.run(host="0.0.0.0", port=port)

