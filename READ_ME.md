#inventory service
an http service that tracks how many copies of video games are in-stock or out-of-stock.

#what it does
- adds a game to the inv with a starting quantity
- list items or look up by its key (id)
- increase/decrease stock
- reject any duplicates or negative stock
- delete items
- saves data in sqlite file to survive restart

#requirements
- python3
- linux, macOS, or windows

#setup
"
git clone https://github.com/[your-user]/inventory-service.git
cd inventory_service
python3 -m venv .venv
source .venv/bin/activate
pip install -r packages.txt
"

#run
"
uvicorn main:app --reload
"

this inventory service is ran at "http://127.0.0.1:8000"
interactive docs: "http://127.0.0.1:8000/docs"

#endpoints
get, '/', check if up, 200
post, '/items', create item, 201, 409(dupe), 422(bad)
get, '/items', list items, 200
get, '/items/{key}, get one item, 200, 404(not found)
delete, '/items/{key}, delete item, 204, 404(not found)
post, '/items/{key}/adjustments', increase or decrease stock, 200, 400(not enough), 404(not found), 422(bad)

#format
"json
{
	"key":"zelda1"
	"name":"Zelda",
	"quantity": 5
}
"
-"key": unique ID for game
-"name": game title
-"quantity": copies in stock

#examples
create item:
"
curl -X POST http://127.0.0.1:8000/items -H "Content-Type: application/json" -d '{"key":"zelda1","name":"Zelda","quantity":5}'
"
add 2 copies:
"
curl -X POST http://127.0.0.1:8000/items/zelda1/adjustments -H "Content-Type: application/json" -d '{"change": 2}'
"
remove 2 copies:
"
curl -X POST http://127.0.0.1:8000/items/zelda1/adjustments -H "Content-Type: application/json" -d '{"change": -2}'
"
list all items:
"
curl http://127.0.0.1:8000/items
"

#how the changes work
the adjustments use a single sql 'update' that only runs if the result stays at 0 or above. this keeps the stock from going negative.

#service structure
"
inventory_service/
	main.py (service)
	packages.txt (dependencies)
	inventory.db (created auto on first run)
	READ_ME.md
"
