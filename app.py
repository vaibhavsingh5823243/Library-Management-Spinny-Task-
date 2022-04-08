from datetime import datetime

from flask import Flask, request, json,render_template,make_response,jsonify

from database import BookDatabase, TransactionDataBase

app = Flask(__name__)

obj = BookDatabase()
transactionObj = TransactionDataBase()

@app.route("/",methods=['GET'])
def index():
    #print("Request comming from outside")
    return render_template('library.html')

@app.route("/books",methods=['GET'])
def bookIndex():
    return render_template('books.html')

@app.route("/transaction",methods=['GET'])
def transactionIndex():
    return render_template('transaction.html')

@app.route("/getData", methods=['POST'])
def getData():
    if request.is_json:
        bookInfo = request.json

        response = obj.insert(bookInfo)
        if response:
            return "Data inserted successfully."
        else:
            return "Some error occurred please try after sometime"


@app.route("/getByRent", methods=['POST','GET'])
def getByRent():
    if request.is_json:
        rent = int(request.json['rentPerDay'])
        data = obj.fetchByRent(rent)
        res = make_response(jsonify(data), 200)
        return res


@app.route("/getByName", methods=['POST','GET'])
def getByName():
    if request.is_json:
        name = request.json['bookName']
        data = obj.fetchByNameTerm(name)
        res=make_response(jsonify(data),200)
        return res


@app.route("/getByNameRentCategory", methods=['POST','GET'])
def getByNameRentCategory():
    #print("Vaibhav")

    if request.is_json:
        queryData = request.json
        data = obj.fetchByNameRentCategory(queryData)
        res = make_response(jsonify(data), 200)
        return res


@app.route("/issueBook", methods=['POST'])
def issueBook():
    if request.is_json:
        data = request.json
        response = transactionObj.insert(data)
        info={}
        if response:
            info['message']="Book issued successfully."
        else:
            info['message']="No such book available"
        #print(info)
        res=make_response(jsonify(info),200)
        return res

@app.route("/returnBook", methods=["POST"])
def returnBook():
    if request.is_json:
        data = request.json
        response = transactionObj.update(data)
        info = {}
        if response:
            info['message'] = "Book return successfully."
        else:
            info['message'] = "No such book issued earlier"
        #print(info)

        res = make_response(jsonify(info), 200)
        return res


@app.route("/totalRent", methods=["POST"])
def totalRent():
    if request.is_json:
        bookName = request.json['bookName']
        data = transactionObj.getTotalRent(bookName)
        #print(data)
        res=make_response(jsonify(data),200)
        return res

@app.route("/totalBook", methods=['POST'])
def totalBook():
    if request.is_json:
        personName = request.json['personName']
        data = transactionObj.getAllBooks(personName)
        #print(data)

        res=make_response(jsonify(data),200)
        return res


@app.route("/issuedBooks", methods=['POST'])
def issuedBooks():
    if request.is_json:
        date = datetime.strptime(request.json['dates'], "%d-%M-%Y")
        booksInfo = transactionObj.issuedBooks(date)
        res=make_response(jsonify(booksInfo),200)
        return res


@app.route("/personList", methods=["POST"])
def personList():
    if request.is_json:
        bookName = request.json['bookName']
        data = transactionObj.getAllPerson(bookName)
        #print(data)

        res=make_response(jsonify(data),200)
        return res


if __name__ == '__main__':
    app.run()
