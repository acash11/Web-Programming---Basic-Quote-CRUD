from flask import Flask, render_template, request, make_response, redirect
from mongita import MongitaClientDisk
from bson import ObjectId
from passwords import hash_password #password
from passwords import check_password #password

app = Flask(__name__)

# create a mongita client connection
client = MongitaClientDisk()

# open the quotes database
quotes_db = client.quotes_db
session_db = client.session_db
user_db = client.user_db

import uuid

#Clears all entries. In a real application, this would obviously not exist
#@app.route("/d", methods=["GET"])
#def delete_collections():
#    session_collection = session_db.session_collection
#    session_collection.delete_many({})
#    user_collection = user_db.user_collection
#    user_collection.delete_many({})
#    quotes_collection = quotes_db.quotes_collection
#    quotes_collection.delete_many({})
#
#    return redirect("/login")


@app.route("/", methods=["GET"])
@app.route("/quotes", methods=["GET"])
def get_quotes():
    session_id = request.cookies.get("session_id", None)
    if not session_id:
        response = redirect("/login")
        return response
    # open the session collection
    session_collection = session_db.session_collection
    # get the data for this session
    session_data = list(session_collection.find({"session_id": session_id}))
    if len(session_data) == 0:
        response = redirect("/logout")
        return response
    assert len(session_data) == 1
    session_data = session_data[0]
    # get some information from the session
    user = session_data.get("user", "unknown user")
    # open the quotes collection
    quotes_collection = quotes_db.quotes_collection
    # load the data
    data = list(quotes_collection.find({"owner":user}))

    ###
    public_data = list(quotes_collection.find({"view":"Public"}))
    ###


    for item in data:
        item["_id"] = str(item["_id"])
        item["object"] = ObjectId(item["_id"])

    ###
    for item in public_data:
        item["_id"] = str(item["_id"])
        item["object"] = ObjectId(item["_id"])
    ###

    # display the data
    html = render_template(
        "quotes.html",
        data=data,
        user=user,
        public_data=public_data
    )
    response = make_response(html)
    response.set_cookie("session_id", session_id)
    return response


@app.route("/login", methods=["GET"])
def get_login():
    session_id = request.cookies.get("session_id", None)
    print("Pre-login session id = ", session_id)
    if session_id:
        return redirect("/quotes")
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def post_login():
    user = request.form.get("user", "")
    password = request.form.get("password", "")
    # open the user collection
    user_collection = user_db.user_collection
    # look for the user
    print(list(user_collection.find({"user": user})))
    user_data = list(user_collection.find({"user": user}))
    if len(user_data) != 1:
        response = redirect("/login")
        response.delete_cookie("session_id")
        return response
    
    hashed_password = user_data[0].get("hashed_password", "")
    salt = user_data[0].get("salt", "")
    print(hashed_password)
    print(salt)
    print(check_password(password, hashed_password, salt))

    if check_password(password, hashed_password, salt) == False:
        response = redirect("/login")
        response.delete_cookie("session_id")
        return response


    session_id = str(uuid.uuid4())
    # open the session collection
    session_collection = session_db.session_collection
    # insert the user
    session_collection.delete_one({"session_id": session_id})
    session_data = {"session_id": session_id, "user": user}
    session_collection.insert_one(session_data)
    response = redirect("/quotes")
    response.set_cookie("session_id", session_id)
    return response

@app.route("/register", methods=["GET"])
def get_register():
    session_id = request.cookies.get("session_id", None)
    print("Pre-login session id = ", session_id)
    if session_id:
        return redirect("/quotes")
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def post_register():
    user = request.form.get("user", "")
    password = request.form.get("password", "")
    password2 = request.form.get("password2", "")
    if password != password2:
        response = redirect("/register")
        response.delete_cookie("session_id")
        return response
    
    # open the user collection
    user_collection = user_db.user_collection
    # look for the user
    user_data = list(user_collection.find({"user": user}))
    if len(user_data) == 0:
        hash = hash_password(password)
        user_data = {"user": user, "hashed_password": hash[0], "salt": hash[1]}
        user_collection.insert_one(user_data)

    response = redirect("/login")
    response.delete_cookie("session_id")
    return response


@app.route("/logout", methods=["GET"])
def get_logout():
    # get the session id
    session_id = request.cookies.get("session_id", None)
    if session_id:
        # open the session collection
        session_collection = session_db.session_collection
        # delete the session
        session_collection.delete_one({"session_id": session_id})
    response = redirect("/login")
    response.delete_cookie("session_id")
    return response


@app.route("/add", methods=["GET"])
def get_add():
    session_id = request.cookies.get("session_id", None)
    if not session_id:
        response = redirect("/login")
        return response
    return render_template("add_quote.html")


@app.route("/add", methods=["POST"])
def post_add():
    session_id = request.cookies.get("session_id", None)
    if not session_id:
        response = redirect("/login")
        return response
    # open the session collection
    session_collection = session_db.session_collection
    # get the data for this session
    session_data = list(session_collection.find({"session_id": session_id}))
    if len(session_data) == 0:
        response = redirect("/logout")
        return response
    assert len(session_data) == 1
    session_data = session_data[0]
    # get some information from the session
    user = session_data.get("user", "unknown user")
    text = request.form.get("text", "")
    author = request.form.get("author", "")
    view = request.form.get("view", "")
    if text != "" and author != "":
        # open the quotes collection
        quotes_collection = quotes_db.quotes_collection
        # insert the quote
        quote_data = {"owner": user, "text": text, "author": author, "view": view}
        quotes_collection.insert_one(quote_data)
    # usually do a redirect('....')
    return redirect("/quotes")


@app.route("/edit/<id>", methods=["GET"])
def get_edit(id=None):
    session_id = request.cookies.get("session_id", None)
    if not session_id:
        response = redirect("/login")
        return response
    if id:
        #Check if user owns this quote!
        #From the session_id, get the user
        session_collection = session_db.session_collection
        #From the quote_id, get the author
        #Compare the two
        session_data = list(session_collection.find({"session_id": session_id}))
        if len(session_data) == 0:
            response = redirect("/logout")
            return response
        assert len(session_data) == 1
        session_data = session_data[0]
        check_user1 = session_data.get("user", "")   

        # open the quotes collection
        quotes_collection = quotes_db.quotes_collection
        # get the item
        data = quotes_collection.find_one({"_id": ObjectId(id)})

        check_user2 = data.get("owner", "")

        if not check_user1 == check_user2:
            return "<h1>Wait a minute! You don't own this quote!</h1>"

        data["id"] = str(data["_id"])
        return render_template("edit_quote.html", data=data)
    # return to the quotes page
    return redirect("/quotes")


@app.route("/edit", methods=["POST"])
def post_edit():
    session_id = request.cookies.get("session_id", None)
    if not session_id:
        response = redirect("/login")
        return response
    _id = request.form.get("_id", None)
    text = request.form.get("text", "")
    author = request.form.get("author", "")
    view = request.form.get("view", "")
    if _id:
        #Check if user owns this quote!
        #From the session_id, get the user
        session_collection = session_db.session_collection
        #From the quote_id, get the author
        #Compare the two
        session_data = list(session_collection.find({"session_id": session_id}))
        if len(session_data) == 0:
            response = redirect("/logout")
            return response
        assert len(session_data) == 1
        session_data = session_data[0]
        check_user1 = session_data.get("user", "")


        # open the quotes collection
        quotes_collection = quotes_db.quotes_collection
        # get the item
        data = quotes_collection.find_one({"_id": ObjectId(_id)})

        check_user2 = data.get("owner", "")

        if not check_user1 == check_user2:
            return "<h1>Wait a minute! You don't own this quote!</h1>"
        

        # update the values in this particular record
        values = {"$set": {"text": text, "author": author, "view": view}}
        data = quotes_collection.update_one({"_id": ObjectId(_id)}, values)
    # do a redirect('....')
    return redirect("/quotes")


@app.route("/delete", methods=["GET"])
@app.route("/delete/<id>", methods=["GET"])
def get_delete(id=None):
    session_id = request.cookies.get("session_id", None)
    if not session_id:
        response = redirect("/login")
        return response
    if id:
        #Check if user owns this quote!
        #From the session_id, get the user
        session_collection = session_db.session_collection
        #From the quote_id, get the author
        #Compare the two
        session_data = list(session_collection.find({"session_id": session_id}))
        if len(session_data) == 0:
            response = redirect("/logout")
            return response
        assert len(session_data) == 1
        session_data = session_data[0]
        check_user1 = session_data.get("user", "")   

        # open the quotes collection
        quotes_collection = quotes_db.quotes_collection
        # get the item
        data = quotes_collection.find_one({"_id": ObjectId(id)})

        check_user2 = data.get("owner", "")

        if not check_user1 == check_user2:
            return "<h1>Wait a minute! You don't own this quote!</h1>"


        # delete the item
        quotes_collection.delete_one({"_id": ObjectId(id)})
    # return to the quotes page
    return redirect("/quotes")

if __name__ == '__main__':
    app.run()