Updated 09/04/2021

export FLASK_APP=server.py && flask run --host=0.0.0.0


0) curl 'localhost:5000/registerShieldingIndividual?CHI=42'

Returns: ["EH9 8LQ","fwjwvwm","wduvgavy","9110026109013"] ([postcode, name, surname, phone number]) / already registered

1) curl 'localhost:5000/showFoodBox?[dietaryPreference=none']

Returns: [{"contents":[{"id":1,"name":"cucumbers","quantity":1},{"id":2,"name":"tomatoes","quantity":2},{"id":6,"name":"pork","quantity":1}],"delivered_by":"catering","diet":"none","id":1,"name":"box a"},{"contents":[{"id":3,"name":"onions","quantity":1},{"id":4,"name":"carrots","quantity":2},{"id":8,"name":"bacon","quantity":1}],"delivered_by":"catering","diet":"none","id":3,"name":"box c"},{"contents":[{"id":13,"name":"cabbage","quantity":1},{"id":11,"name":"avocado","quantity":1},{"id":8,"name":"bacon","quantity":1},{"id":9,"name":"oranges","quantity":1}],"delivered_by":"catering","diet":"none","id":4,"name":"box d"}]

2) curl --request POST -d '{"contents": [{"id":1,"name":"cucumbers","quantity":20},{"id":2,"name":"tomatoes","quantity":2}]}' -H 'Content-Type: application/json' 'localhost:5000/placeOrder?individual_id=42&catering_business_name=catering1&catering_postcode=eh0112'

Returns order_id

3) curl --request POST -d '{"contents": [{"id":1,"name":"cucumbers","quantity":19},{"id":2,"name":"tomatoes","quantity":2}]}' -H 'Content-Type: application/json' 'localhost:5000/editOrder?order_id=14'

Returns True or False

4) curl 'localhost:5000/requestStatus?order_id=42'

Returns status integer or -1 if order not found

5) curl 'localhost:5000/registerCateringCompany?business_name=catering1&postcode=eh0111'

(The server does not verify the postcode. This means that the postcode can be almost anything)
Returns: registered new / already registered

6) curl 'localhost:5000/cancelOrder?order_id=42'

Returns: true or false

7) curl 'localhost:5000/registerSupermarket?business_name=catering1&postcode=eh0111'

(The server does not verify the postcode. This means that the postcode can be almost anything)
Returns: registered new / already registered

8) curl 'localhost:5000/updateOrderStatus?order_id=42&newStatus=packed' (packed/dispatched/delivered)

Returns: True or False

9) curl 'localhost:5000/getCaterers'

Returns: ["catering1,eh0111","catering1,eh0111","catering1,eh0111","catering1,eh0111","catering1,eh0111","catering1,eh0111","catering1,eh0112","catering1,eh0113","catering1,eh0114"]

10) curl 'localhost:5000/distance?postcode1=EH11_2DR&postcode2=EH11_3DR' (Only 'EH')

Returns: 17.477597712106768 (in meters [not actual distance])

11) curl 'localhost:5000/recordSupermarketOrder?individual_id=42&order_number=42&supermarket_business_name=catering1&supermarket_postcode=eh0111'

Returns:
True or error message

12) curl 'localhost:5000/updateSupermarketOrderStatus?order_id=420&newStatus=packed'

Returns:
True or False
