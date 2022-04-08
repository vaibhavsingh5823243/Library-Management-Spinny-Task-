import re
from datetime import datetime

import pymongo as pym


class BookDatabase:

    def __init__(self, bookDbName='Books'):
        self.conn = pym.MongoClient(
            "mongodb+srv://vaibhav:vaibhav@cluster0.umxqg.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
        self.bookDb = self.conn[bookDbName]

    def insert(self, data):
        try:
            coll = self.bookDb['bookinfo']
            coll.insert_one(data)
            return True

        except Exception as e:
            return False

    def filter(self, data):
        try:
            coll = self.bookDb['bookinfo']
            bnPattern = re.compile(data, re.IGNORECASE)
            rent = coll.find_one({"bookName": {"$regex": bnPattern}}, {"_id": 0, "rentPerDay": 1})
            if rent:
                return rent['rentPerDay']
            return 0
        except Exception as e:
            raise e

    def fetchByRent(self, rent):
        try:
            coll = self.bookDb['bookinfo']
            booksObj = coll.find({"rentPerDay": {"$lte": rent}}, {"_id": 0})
            books = [i for i in booksObj]
            return books
        except Exception as e:
            return "No data available"

    def fetchByNameTerm(self, name):
        try:
            coll = self.bookDb['bookinfo']
            pattern = re.compile(name, re.IGNORECASE)
            booksObj = coll.find({"bookName": {"$regex": pattern}}, {"_id": 0})
            books = [i for i in booksObj]
            return books
        except Exception as e:
            raise e

    def fetchByNameRentCategory(self, queryData):
        try:
            coll = self.bookDb['bookinfo']
            catPattern = re.compile(queryData['category'],re.IGNORECASE)
            bnPattern = re.compile(queryData['bookName'], re.IGNORECASE)
            booksObj = coll.find({"$and": [{"bookName": {"$regex": bnPattern}}, {"category": {"$regex": catPattern}},
                                           {"rentPerDay": {"$lte": int(queryData['rentPerDay'])}}]}, {"_id": 0})
            books = [i for i in booksObj]
            return books
        except Exception as e:
            raise e


class TransactionDataBase(BookDatabase):
    def __init__(self, transactionDbName='Transaction'):
        super().__init__()
        self.conn = self.conn
        self.transactionDb = self.conn[transactionDbName]

    def insert(self, data):
        try:
            rentPerDay = self.filter(data['bookName'])
            if rentPerDay:
                coll = self.transactionDb['transactionInfo']
                data['issueDate'] = datetime.strptime(data['issueDate'], "%d-%M-%Y")
                data['returnDate'] = -1
                data['rent'] = 0
                coll.insert_one(data)
                return True
            return False
        except Exception as e:
            raise e

    def update(self, data):
        try:
            coll = self.transactionDb['transactionInfo']
            data['returnDate'] = datetime.strptime(data['returnDate'], "%d-%M-%Y")
            pnPattern = re.compile(data['personName'], re.IGNORECASE)
            bnPattern = re.compile(data['bookName'], re.IGNORECASE)
            issueDate = coll.find_one(
                {"$and": [{"personName": {"$regex": pnPattern}}, {"bookName": {"$regex": bnPattern}},
                          {"returnDate": {"$eq": -1}}]}, {"issueDate": 1, "_id": 0})
            if issueDate:
                noOfDays = (data['returnDate'] - issueDate['issueDate']).days
                rentPerDay = self.filter(data['bookName'])
                rent = rentPerDay * noOfDays
                coll.update({"$and": [{"personName": {"$regex": pnPattern}}, {"bookName": {"$regex": bnPattern}},
                                      {"returnDate": {"$eq": -1}}]},
                            {"$set": {"returnDate": data['returnDate'], "rent": rent}})
                return True
            return False
        except Exception as e:
            return False

    def getTotalRent(self, bookName):
        try:
            coll = self.transactionDb['transactionInfo']
            bnPattern = re.compile(bookName, re.IGNORECASE)
            bookRentObj = coll.aggregate([{"$match": {"bookName": {"$regex": bnPattern}}},
                                          {"$group": {"_id": "$bookName", "TotalRent": {"$sum": "$rent"}}}])
            totalRent = [book for book in bookRentObj]
            return totalRent[0]
        except Exception as e:
            #print(e)
            return False

    def getAllBooks(self, personName):
        try:
            coll = self.transactionDb['transactionInfo']
            pnPattern = re.compile(personName, re.IGNORECASE)
            booksObj = coll.find({"personName": pnPattern}, {"_id": 0, "bookName": 1})
            books = [book for book in booksObj]
            return books
        except Exception as e:
            return False

    def issuedBooks(self, date):
        try:
            coll = self.transactionDb['transactionInfo']

            bookObj = coll.find({"issueDate": {"$lte": date}}, {"_id": 0, "bookName": 1, "personName": 1})
            data=[i for i in bookObj]
            return data
        except Exception as e:
            return False

    def getAllPerson(self, bookName):
        try:
            coll = self.transactionDb['transactionInfo']
            bnPattern = re.compile(bookName, re.IGNORECASE)
            personObj = coll.find({"bookName": {"$regex": bnPattern}}, {"_id": 0, "personName": 1})
            currentPersonObj = coll.find({"$and": [{"bookName": {"$regex": bnPattern}}, {"returnDate": {"$eq": -1}}]},
                                         {"_id": 0, "personName": 1})
            person = [per['personName'] for per in personObj]
            currentPerson = [per['personName'] for per in currentPersonObj]
            data={"IssuedBooks":person,"CurrentlyIssued":currentPerson}
            return data
        except Exception as e:
            return False
