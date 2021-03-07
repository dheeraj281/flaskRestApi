import markdown, os, sqlite3, json
from flask import Flask, Response
from flask_restful import Resource, Api, reqparse


app = Flask(__name__)
api = Api(app)


@app.route("/")
def index():
    with open(os.path.dirname(app.root_path) + '/README.md', 'r') as markdown_file:
        content = markdown_file.read()
        return markdown.markdown(content)


def db_connection():
    conn = None
    try:
        conn = sqlite3.connect("books.sqlite")
    except sqlite3.error as e:
        print(e)
    return conn

def execute_sql_cmd(cmdtype, args=None):
    conn = db_connection()
    cursor = conn.cursor()

    if cmdtype == "fetch_all":
        cursor.execute("SELECT * FROM books")
        data = [dict(id=row[0], author=row[1], language=row[2], title=row[3]) for row in cursor.fetchall()]

    if cmdtype == "insert":
        sql = """INSERT INTO books (author, language, title) VALUES (?, ?, ?)"""
        cursor.execute(sql,args)
        new_id = cursor.lastrowid
        cursor.execute('SELECT * FROM books WHERE id=?', (new_id,))
        data = cursor.fetchone()
        conn.commit()

    if cmdtype == "get_book":
        cursor.execute("SELECT * FROM books WHERE id=?", (args,))
        data = cursor.fetchone()


    if cmdtype == "update":
        sql = """UPDATE books SET title=?, author=?, language=? WHERE id=? """
        cursor.execute(sql, args)
        conn.commit()
        cursor.execute('SELECT * FROM books WHERE id=?', (args[-1],))
        data = cursor.fetchone()


    if cmdtype == "delete":
        sql = """ DELETE FROM books WHERE id=? """
        cursor.execute(sql, (args,))
        conn.commit()
        cursor.execute('SELECT * FROM books WHERE id=?', (args,))
        book = cursor.fetchone()
        data = True if book == None else False

    if conn:
        print("Request fulfilled. closing database connection")
        conn.close()
        path = os.path.abspath('temp.db')

    return data




class booklist(Resource):

    def get(self):
        books = execute_sql_cmd("fetch_all")
        if len(books) > 0:
            return {'message': 'Success', 'data': books}, 200
        else:
            return 'No Content Found', 404


    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('author', type=str, required=True, help="author cannot be blank!")
        parser.add_argument('title', type=str, required=True, help="title cannot be blank!")
        parser.add_argument('language', type=str, required=True, help="language cannot be blank!")
        # Parse the arguments into an object
        args = parser.parse_args()
        new_entry = execute_sql_cmd("insert",(args['author'], args['language'], args['title']))
        data = {'message': 'book registered','data': {'id': new_entry[0],'author':new_entry[1], 'language': new_entry[2], 'title':new_entry[3]}}
        response = Response(response=json.dumps(data),status=201,mimetype='application/json')
        return response



class book(Resource):

    def get(self, id):
        book = execute_sql_cmd("get_book",id)
        if book is not None:
            data= {'message':'Success', 'data':{'id': book[0],'author':book[1], 'language': book[2], 'title':book[3]}}
            response = Response(response=json.dumps(data),status=200,mimetype='application/json')
        else:
            data = {'message': 'Book not found', 'data': {}}
            response = Response(response=json.dumps(data), status=404, mimetype='application/json')
        return response

    def put(self, id):
        book = execute_sql_cmd("get_book", id)
        if book is not None:
            parser = reqparse.RequestParser()
            parser.add_argument('author', type=str, required=True, help="author cannot be blank!")
            parser.add_argument('title', type=str, required=True, help="title cannot be blank!")
            parser.add_argument('language', type=str, required=True, help="language cannot be blank!")
            # Parse the arguments into an object
            args = parser.parse_args()
            updated = execute_sql_cmd("update",(args['title'], args['author'], args['language'], id))
            data = {'message': 'Success', 'data': {'id': updated[0], 'author': updated[1], 'language': updated[2], 'title': updated[3]}}
            response = Response(response=json.dumps(data), status=200, mimetype='application/json')
        else:
            data = {'message': 'Book not found', 'data': {}}
            response = Response(response=json.dumps(data), status=404, mimetype='application/json')
        return response

    def delete(self, id):
        book = execute_sql_cmd("get_book", id)
        if book is not None:
            if execute_sql_cmd("delete",id):
                return "The book with id: {} has been deleted.".format(id), 204
            else:
                data = {'message': 'Something went wrong. Try again later'}
                response = Response(response=json.dumps(data), status=500, mimetype='application/json')
                return response
        else:
            data = {'message': 'Book not found', 'data': {}}
            response = Response(response=json.dumps(data), status=404, mimetype='application/json')
            return response

api.add_resource(booklist, '/books')
api.add_resource(book, '/books/<string:id>')
