from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
#cnt = 0

class Tiny(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    longurl = db.Column(db.String(100))
    shorturl = db.Column(db.String(100))
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

def encode_short_url(unique_id):
    base_62 = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    res_string = 'https://www.shorturl.com/'
    while unique_id > 0:
        res_string += base_62[unique_id % 62]
        unique_id = unique_id // 62
    return res_string

def first_missing_id(nums):
    if 1 not in nums:
        return 1
    
    for i in range(len(nums)):
        if nums[i] > len(nums):
            nums[i] = 1
    
    for i in range(len(nums)):
        curr_number = abs(nums[i])
        if curr_number == len(nums):
            nums[0] = -abs(nums[0])
        else:
            nums[curr_number] = -abs(nums[curr_number])
    for i in range(1, len(nums)):
        if nums[i] > 0:
            return i
    if nums[0] > 0:
        return len(nums)
    
    return len(nums) + 1

def remove_tuple(id_list):
    res = []
    for id in id_list:
        res.append(int(str(id)[1:-2]))
    return res

@app.route('/')
def index():
    tiny_list = Tiny.query.all()
    #print(tiny_list)
    #print(len(Tiny.query.all()))
    # [(1,), (3,), (4,), (5,)]
    #print(Tiny.query.with_entities(Tiny.id).all())
    return render_template('base.html', tiny_list=tiny_list)


@app.route('/convert',methods=['POST'])
def convert():
    #global cnt
    #cnt += 1
    #cnt = len(Tiny.query.all()) + 1
    id_list = remove_tuple(Tiny.query.with_entities(Tiny.id).all())
    cnt = first_missing_id(id_list)
    longurl = request.form.get('url')
    name = request.form.get('name')
    email = request.form.get('email')
    shorturl = encode_short_url(cnt)
    new_tiny = Tiny(longurl=longurl, shorturl = shorturl, name=name, email=email)
    db.session.add(new_tiny)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/delete/<int:tiny_id>')
def delete(tiny_id):
    tiny = Tiny.query.filter_by(id=tiny_id).first()
    db.session.delete(tiny)
    db.session.commit()
    return redirect(url_for('index'))
    
if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)