from flask import Flask, render_template, request, url_for, jsonify, make_response, redirect
import jwt
from werkzeug.security import check_password_hash
from psycopg2.extras import RealDictCursor
import psycopg2
import os
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY')
admin_user = os.getenv('ADMIN_USER')
admin_password_hash = os.getenv('ADMIN_PASSWORD_HASH')
db_url = os.getenv('DATABASE_URL')

def get_connection():
    return psycopg2.connect(db_url)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS posts (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    txt TEXT NOT NULL
                )''')
    conn.commit()
    cur.close()
    conn.close()


def get_posts():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, title, txt FROM posts')
        rows = cur.fetchall()
    except Exception as e:
        print("Error:", e)
        rows = []
    finally:
        cur.close()
        conn.close()
    return rows

def run_sql(querie, parameters=None, get_id=False):
    conn = get_connection()
    cur = conn.cursor()
    if parameters:
        cur.execute(querie, parameters)
    else:
        cur.execute(querie)
    conn.commit()
    lpost_id = cur.fetchone()[0] if get_id else None
    cur.close()
    conn.close()
    return lpost_id













@app.route('/')
def home():
    posts = get_posts()
    if len(posts)>=3:
        Wposts = [posts[-1], posts[-2], posts[-3]]
    else:
        Wposts = []
        for i in range(len(posts)):
            Wposts.append(posts[-i - 1])        
    return render_template('index.html', Wposts=Wposts) 

@app.route('/posts')
def posts():
    Rposts = get_posts()
    posts = list(reversed(Rposts))
    return render_template('posts.html', posts=posts)

@app.route('/projects')
def projects():
    return render_template('my_projects.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/read/<int:PostId>')
def read(PostId):
    posts = get_posts()
    for post in posts:
        if post[0] == PostId:
            Spost = post
    return render_template('read.html', Spost=Spost)














@app.route('/admin')
def admin():
    token = request.cookies.get('auth_token')
    if token:
        try:
            payload = jwt.decode(token, app.secret_key, algorithms=["HS256"])
            user = payload['user']
            if user == admin_user:              
                Sposts = get_posts()
                posts = list(reversed(Sposts))
                return render_template('admin.html', posts=posts)
            else:
                return redirect(url_for('loginform'))
        except jwt.ExpiredSignatureError:
            return redirect(url_for('loginform'))
        except jwt.InvalidTokenError:
            return redirect(url_for('loginform'))
        except Exception as e:
            return f"error {e}", 500
    else:
        return redirect(url_for('loginform'))

@app.route('/adminlogin')
def loginform():  
    return render_template('admin_login.html')

@app.route('/login', methods=["POST"])
def login():
    data = request.get_json()
    user, password = data['user'], data['password']

    if admin_password_hash is None and admin_user is None:
        return make_response('0') 

    if check_password_hash(admin_password_hash, password) and user == admin_user:
        payload = {'user': admin_user}
        token = jwt.encode(payload, app.secret_key, algorithm="HS256")
        response = make_response('1')
        response.set_cookie(
            "auth_token",   
            token,          
            httponly=True,  
            secure=True,  
            samesite="Strict",
            max_age=7200
        ) 
    else:
        print(admin_user, admin_password_hash)
        response = make_response('0')

    return response










@app.route('/delete/<int:postId>', methods=['POST'])
def delete(postId):
    token = request.cookies.get('auth_token')
    if token:
        try:
            run_sql('DELETE FROM posts WHERE id=%s', (postId,))
            return jsonify({'ok': True})
        except jwt.ExpiredSignatureError:
            return redirect(url_for('loginform'))
        except jwt.InvalidTokenError:
            return redirect(url_for('loginform'))
        except Exception as e:
            return f"error {e}", 500
    else:
        return redirect(url_for('loginform'))

@app.route('/share', methods=['POST'])
def share():
    token = request.cookies.get('auth_token')
    if token:
        try:
            data = request.get_json()
            title, txt = data['title'], data['txt']
            PostId = run_sql('INSERT INTO posts (title, txt) VALUES (%s, %s) RETURNING id', (title, txt), True)
            return jsonify({'ok': True, 'PostId': PostId})
        except jwt.ExpiredSignatureError:
            return redirect(url_for('loginform'))
        except jwt.InvalidTokenError:
            return redirect(url_for('loginform'))
        except Exception as e:
            return f"error {e}", 500
    else:
        return redirect(url_for('loginform'))
    

@app.route('/UpdateForm/<int:PostId>')
def UpdateForm(PostId):
    token = request.cookies.get('auth_token')
    if token:
        try:
            posts = get_posts()
            for post in posts:
                if post[0] == PostId:
                    Spost = post
            return render_template('update.html', Spost=Spost)
        except jwt.ExpiredSignatureError:
            return redirect(url_for('loginform'))
        except jwt.InvalidTokenError:
            return redirect(url_for('loginform'))
        except Exception as e:
            return f"error {e}", 500
    else:
        return redirect(url_for('loginform'))

@app.route('/Update', methods=['POST'])
def Update():
    token = request.cookies.get('auth_token')
    if token:
        try:
            data = request.get_json()
            Uptitle, Uptxt, PostId = data['Uptitle'], data['Uptxt'], data['PostId']
            run_sql('UPDATE posts SET title=%s, txt=%s WHERE id=%s', (Uptitle, Uptxt, PostId))
            return jsonify({'ok':True})
        except jwt.ExpiredSignatureError:
            return redirect(url_for('loginform'))
        except jwt.InvalidTokenError:
            return redirect(url_for('loginform'))
        except Exception as e:
            return f"error {e}", 500
    else:
        return redirect(url_for('loginform'))

if __name__ == '__main__':
    app.run(debug=True)