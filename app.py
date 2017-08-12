from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import Flask,render_template,jsonify,json,request
app = Flask(__name__, static_url_path='/static')
app.debug = True
 
#this is test
client = MongoClient('localhost:27017')



@app.route("/")
def home():
    return app.send_static_file("index.html")


@app.route("/data/<name>/<id>")
def details(name,id):
    collectionname = name.split('.',1)[1]
    databasename =name.split('.',1)[0]
    try:
        objs = client[databasename][collectionname].find({"_id" : ObjectId(id)})

    except Exception as e:
        try:
            if id.isdigit():
                objs = client[databasename][collectionname].find({"_id" : int(id)})
            
            elif id.replace('.','',1).isdigit():
                objs = client[databasename][collectionname].find({"_id" : float(id)})
            else:
                objs = client[databasename][collectionname].find({"_id" : id})
        except Exception as e:
            return str(e)
    return jsonify(details=prepareResponse(objs))


@app.route("/menu")
def menu():

    d = dict((db, [db + '.' + collection   for collection in client[db].collection_names()])
             for db in client.database_names())
    return jsonify(list=d)

#test

@app.route("/add/collection/<name>")
def addCollection(name):
    collectionname = name.split('.',1)[1]
    databasename =name.split('.',1)[0]
    post = {}
    d = client[databasename][collectionname].insert_one(post).inserted_id
    client[databasename][collectionname].createIndex( { "$**": "text" } )
    return jsonify(result=prepareResponse(d))


def prepareResponse(objs):
    objList = []
    try:
        for obj in objs:
            objItem = {}
            for n in obj:
                if isinstance(n, ObjectId):
                    objItem[n] = obj[n]
                else:
                    #objItem["Action"] = "<a href='#' onClick='openRecord(\"" + str(obj[n]) + "\")' class='glyphicon glyphicon-chevron-right'></a>"
                    objItem[n] = str(obj[n])
            objList.append(objItem)
    except Exception as e:
        1
    return objList

@app.route("/data/<name>")
def list(name):
    collectionname = name.split('.',1)[1]
    databasename =name.split('.',1)[0]
    
    pageno = request.args.get('pageno')
    if pageno =='':
        pageno = 0
    q = request.args.get('q')
    query= {}
    if len(q)>0:
        query =  { '$text': { '$search': q, '$caseSensitive': True } }
    try:
        objs = client[databasename][collectionname].find(query).skip(int(pageno)*10).limit (10)
    except Exception as e:
        return str(e)
    return jsonify(list=prepareResponse(objs))


if __name__ == "__main__":
    app.run()