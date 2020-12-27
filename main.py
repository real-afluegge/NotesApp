from flask import Flask, request, render_template

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient("mongodb+srv://sqacey:password@cluster0.tmmhm.mongodb.net/notes?retryWrites=true&w=majority")
db = client.test

def encrypt(passw):
    ''' encryption function: encrypts text you input and the outputs the AES encrypted version '''
    data = passw.encode("utf-8")
    key = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_EAX)
    
    ciphertext, tag = cipher.encrypt_and_digest(data)
    
    return key, ciphertext, cipher.nonce, tag


def decrypt(key, nonce, ciphertext, tag):
    ''' decryption function: decrypts the inputed text '''
    cipher = AES.new(key, AES.MODE_EAX, nonce)
    data = cipher.decrypt_and_verify(ciphertext, tag)
    
    return data


@app.route('/')
def home():
    return  render_template("home.html")


@app.route('/create', methods =["GET", "POST"])
def note():
   return render_template("create.html")


@app.route('/login', methods = ["GET", "POST"])
def login():
    return render_template("login.html")


@app.route('/result', methods = ["GET", "POST"])
def result():
   if request.method == 'POST':
      
      user = request.form.get("user")
      password = request.form.get("pass")
      note = request.form.get("note")
      color = request.form.get("color")
      
      articles = db.articles

      key, encryptPass, nonce, tag = encrypt(password)
      decryptPass = decrypt(key, nonce, encryptPass, tag).decode("utf-8")
      
      vals = [user, note]
      
      article = {"user": user,
                 "pass": encryptPass,
                 "note": note,
                 "color": color,
                 "decoder": [key, nonce, tag]}
      
      articles.insert_one(article)
      
      return render_template("output.html", result=vals, color=color)


@app.route('/notes', methods=["GET", "POST"])
def notes():
    if request.method == 'POST':
        user = request.form.get("loguser")
        password = request.form.get("logpass")
        
        articles = db.articles
        
        yeet = articles.find({"user": user})
        for one in yeet:
            query = one
        decryptPass = decrypt(query["decoder"][0], query["decoder"][1], query["pass"], query["decoder"][2]).decode("utf-8")
        if decryptPass == password:
            vals = [query["user"], query["note"]]
            return render_template("output.html", result=vals, color=query["color"])
        else:
            return "hah fucking idiot forgot their password"
    

if __name__=="__main__":
    app.config["DEBUG"] = True
    app.run()
