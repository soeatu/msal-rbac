from flask import Flask, redirect, url_for, session, request
import msal
import uuid
from functools import wraps
from flask import abort
from flask_login import login_user,LoginManager,current_user,login_required,UserMixin



app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = '開発用シークレットキー'
msal_app = msal.ConfidentialClientApplication(CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET)
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    name = "admin"
    role = "admin" # ロール情報を追加

@login_manager.user_loader
def load_user(user_id):
    # ユーザー情報を取得する処理を書く（例えばDBから取得する）
    # ここでは、ユーザー情報のロール情報を取得している。
    current_user.role = "admin" # ロール情報を追加
    user = User()
    user.role = "admin" # ロール情報を追加
    return user
    # return User.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if not session:
        return redirect(url_for('login'))
    return f"Welcome!"


@app.route('/admin')
@admin_required
def adminpage():
    if not session:
        return redirect(url_for('login'))
    return f"Welcome admin!"

@app.route('/login')
def login():
    # 一意のセッション状態を生成
    session['state'] = str(uuid.uuid4())
    # 認証URLを生成
    auth_url = msal_app.get_authorization_request_url(SCOPES, state=session['state'], redirect_uri=url_for('authorized', _external=True, _scheme='https'))
    return redirect(auth_url)

@app.route(REDIRECT_PATH)
def authorized():
    access_token = msal_app.acquire_token_for_client(scopes = SCOPES)
    if access_token:       
         # 認証情報をセッションに保存
        session['user'] = access_token.get('id_token_claims')
        login_user(user, form.remenber_me.data)
        return redirect(url_for('index'))        
    else:
        print('ERROR: No "access_token" in the result.')
   

if __name__ == '__main__':
    app.run(ssl_context='adhoc')  # HTTPS接続で実行するための設定