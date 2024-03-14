from flask import Flask, render_template, request, redirect
from mongita import MongitaClientDisk
from bson import ObjectId

app = Flask(__name__)

# create a mongita client connection
client = MongitaClientDisk()

# open the quotes database
quotes_db = client.quotes_db


@app.route("/", methods=["GET"])
@app.route("/quotes", methods=["GET"])
def get_quotes():
    # open the quotes collection
    quotes_collection = quotes_db.quotes_collection
    # load the data
    data = list(quotes_collection.find({}))
    #print(data)
    for item in data:
        item["_id"] = str(item["_id"])
        item["object"] = ObjectId(item["_id"])
    # display the data
    return render_template("quotes.html", data=data)

@app.route("/delete", methods=["GET"])
@app.route("/delete/<id>", methods=["GET"])
def get_delete(id=None):
    if id:
        # open the quotes collection
        quotes_collection = quotes_db.quotes_collection
        # delete the item
        print("Deleting Quote", list(quotes_collection.find({"_id":ObjectId(id)})))
        quotes_collection.delete_one({"_id":ObjectId(id)})
    # return to the quotes page
    return redirect("/quotes")
    
@app.route('/add', methods=["POST"])
def post_add():
    # open the quotes collection
    quotes_collection = quotes_db.quotes_collection
    # delete the item
    text = request.form.get("text")
    text = text.replace('<', '').replace('>', '')
    author = request.form.get("author")
    entry = {"text":text, "author":author}
    quotes_collection.insert_one(entry)
    # return to the quotes page
    return redirect("/quotes")

@app.route('/edit/<id>', methods=["GET"])
def get_edit(id=None):
    # open the quotes collection
    quotes_collection = quotes_db.quotes_collection
    data = (list(quotes_collection.find({"_id":ObjectId(id)})))[0] 
    print("Editing Quote:", data)
    return render_template("edit.html", data=data)

@app.route('/edit/<id>', methods=["POST"])
def post_edit(id=None):
    # open the quotes collection
    quotes_collection = quotes_db.quotes_collection
    text = request.form.get("text")
    text = text.replace('<', '').replace('>', '')
    author = request.form.get("author")
    #print(id)
    entry = {"text":text, "author":author}
    #print(entry)
    quotes_collection.replace_one({"_id":ObjectId(id)}, entry)

    # return to the quotes page
    return redirect("/quotes")

app.run()