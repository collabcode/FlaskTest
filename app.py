from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import Flask,render_template,jsonify,json,request
app = Flask(__name__, static_url_path='/static')
app.debug = True


client = MongoClient('localhost:27017')
db = client.MachineData


@app.route("/")
def home():
    return app.send_static_file("index.html")


@app.route("/data/<name>/<id>")
def details(name,id):
    try:
        objs = db[name].find({"_id" : ObjectId(id)})

    except Exception as e:
        return str(e)
    return jsonify(details=prepareResponse(objs))


@app.route("/menu")
def menu():

    d = dict((db, [collection for collection in client[db].collection_names()])
             for db in client.database_names())
    return jsonify(list=d)


@app.route("/add/collection/<name>")
def addCollection(name):
    post = {}
    d = db[name].insert_one(post).inserted_id
    return jsonify(result=prepareResponse(d))

def prepareResponse(objs):
    objList = []
    try:
        for obj in objs:
            objItem = {}
            for n in obj:
                if n != "_id":
                    objItem[n] = obj[n]
                else:
                    objItem["Action"] = "<a href='#' onClick='openRecord(\"" + str(obj[n]) + "\")' class='glyphicon glyphicon-chevron-right'></a>"
                    #objItem[n] = str(obj[n])

            objList.append(objItem)
    except Exception as e:
        1
    return objList

@app.route("/data/<name>")
def list(name):
    try:
        objs = db[name].find()
    except Exception as e:
        return str(e)
    return jsonify(list=prepareResponse(objs))


if __name__ == "__main__":
    app.run()