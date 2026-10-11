#store data
import sqlite3

#endpooints anfd error numbers
from fastapi import FastAPI, HTTPException

#basemodel = data = api
from pydantic import BaseModel

#app with title and desc
app = FastAPI(title="Video Game Inventory", description="Keeps track of in-stock or out-of-stock video games.")
DB = "inventory.db"


#connections to database called when endpoint read/change
def connection_get():
	connection = sqlite3.connect(DB)
#dict
	connection.row_factory = sqlite3.Row
	return connection


#item table
def init_db():
#change when end or undo when errr
	with connection_get() as connection:
#create table if doesnt exist
#key=id, name=title, quantity=stock
		connection.execute(
			"""CREATE TABLE IF NOT EXISTS items (
				key TEXT PRIMARY KEY,
				name TEXT NOT NULL,
				quantity INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0)
			)"""
		)


#run when started
init_db()


#request, json sends to api
#add new game
class item(BaseModel):
	key: str
	name: str
	quantity: int = 0

#change game stock
class adjustment(BaseModel):
	change: int


#endpoinmts
#get = chjeck app running
@app.get("/")
def root():
	return {"message": "running"}


#post = add new game
#201 = created
@app.post("/items", status_code=201)
def create_item(_item: item):
	try:
		with connection_get() as connection:
#"?" get filled
			connection.execute(
				"INSERT INTO items (key, name, quantity) VALUES (?, ?, ?)",
				(_item.key, _item.name, _item.quantity),
			)
#database = integrityerror if duplicate or neg
	except sqlite3.IntegrityError:
#409 = conflict
		raise HTTPException(status_code=409, detail="Key exists or is negative")
#new game back to client
	return _item


#get = lists
@app.get("/items")
def list_items():
	with connection_get() as connection:
#select * = all
#fetchall = matching row
		rows = connection.execute("SELECT * FROM items").fetchall()
#row = dict
	return [dict(row) for row in rows]


#get = one game by key
@app.get("/items/{key}")
def get_item(key: str):
	with connection_get() as connection:
#key, = one value
#fetchone = one row or nothing
		row = connection.execute("SELECT * FROM items WHERE key = ?", (key,)).fetchone()
	if row is None:
#404 = doesnt exist
		raise HTTPException(status_code=404, detail="Not found")
	return dict(row)


#delete = remove a game
#204 = successful
@app.delete("/items/{key}", status_code=204)
def delete_item(key: str):
	with connection_get() as connection:
		result = connection.execute("DELETE FROM items WHERE key = ?", (key,))
#rowcount = row query changed
	if result.rowcount == 0:
#0 = nothing deleted doesnt exist
		raise HTTPException(status_code=404, detail="Not found")


#post = add/remove one game
@app.post("/items/{key}/adjustments")
def adjust_stock(key: str, _adjustment: adjustment):
	with connection_get() as connection:
#update quantity
#quantity = quantity + ? adds to current amount
#and quantity + ? >= 0 updates only if new total doesnt drop below 0
		result = connection.execute(
			"UPDATE items SET quantity = quantity + ? WHERE key = ? AND quantity + ? >= 0",
			(_adjustment.change, key, _adjustment.change),
		)
#no row updated = why (error)
		if result.rowcount == 0:
#exists?
			exists = connection.execute("SELECT 1 FROM items WHERE key = ?", (key,)).fetchone()
			if exists is None:
#doesnt exist
				raise HTTPException(status_code=404, detail="Not found")
#key exists = updated failed = neg
#400 = bad request
			raise HTTPException(status_code=400, detail="Not in stock")


#updated worked
		row = connection.execute("SELECT * FROM items WHERE key = ?", (key,)).fetchone()

	return dict(row)
