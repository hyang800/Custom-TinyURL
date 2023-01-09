import sqlite3
from hashids import Hashids
from flask import Flask, render_template, request, flash, redirect, url_for

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def encode_short_url(unique_id):
    base_62 = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    res_string = request.host_url
    while unique_id > 0:
        res_string += base_62[unique_id % 62]
        unique_id = unique_id // 62
    return res_string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'random secret string'
#hashids = Hashids(min_length=4, salt=app.config['SECRET_KEY'])

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()

    if request.method == 'POST':
        url = request.form['url']

        if not url:
            flash('The URL is required!')
            return redirect(url_for('index'))
        
        data_before_insert = conn.execute('select id from urls order by id desc limit 1').fetchone()
        if data_before_insert:
            url_id = dict(data_before_insert)['id'] + 1
        else:
            url_id = 1
        #print(url_id)
        short_url = encode_short_url(url_id)
        
        conn.execute('INSERT INTO urls (original_url, short_url) VALUES (?,?)',
                    (url, short_url))
        conn.commit()
        conn.close()

        return render_template('index.html', short_url=short_url)

    return render_template('index.html')

@app.route('/<id>')
def url_redirect(id):
    conn = get_db_connection()
    short_url = request.host_url + id
    res = conn.execute('select * from urls where short_url = (?)', (short_url,)).fetchone()
    if res:
        original_url = res['original_url']
        clicks = res['clicks']
        original_id = res['id']
        conn.execute('update urls set clicks = ? where id = ?', (clicks+1, original_id))
        conn.commit()
        conn.close()
        return redirect(original_url)
    else:
        flash('Invalid URL')
        return redirect(url_for('index'))

@app.route('/data')
def data():
    conn = get_db_connection()
    urls = conn.execute('select id, created, original_url, short_url, clicks from urls').fetchall()
    conn.close()
    return render_template('data.html', urls=urls)

@app.route('/delete/<id>')
def delete(id):
    conn = get_db_connection()
    #short_url = request.host_url + id 
    conn.execute('delete from urls where id = ?', (id,))
    conn.commit()
    conn.close
    return redirect(url_for('data'))

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port='5000')