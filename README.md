export FLASK_APP=server.py && flask-3.6 run --host=0.0.0.0

curl 129.215.216.19:5000



0) curl '129.215.216.19:5000/registerShieldingIndividual?CHI=42'
Returns: registered new / already registered

1) curl '129.215.216.19:5000/showFoodBox?orderOption=catering&dietaryPreference=none'
Returns: "[{\"id\": 1, \"diet\": \"none\", \"delivered_by\": \"catering\", \"name\": \"box a\", \"contents\": [{\"id\": 1, \"name\": \"cucumbers\", \"quantity\": 1}, {\"id\": 2, \"name\": \"tomatoes\", \"quantity\": 2}, {\"id\": 6, \"name\": \"pork\", \"quantity\": 1}]}, {\"id\": 3, \"name\": \"box c\", \"delivered_by\": \"catering\", \"diet\": \"none\", \"contents\": [{\"id\": 3, \"name\": \"onions\", \"quantity\": 1}, {\"id\": 4, \"name\": \"carrots\", \"quantity\": 2}, {\"id\": 8, \"name\": \"bacon\", \"quantity\": 1}]}, {\"id\": 4, \"name\": \"box d\", \"delivered_by\": \"catering\", \"diet\": \"none\", \"contents\": [{\"id\": 13, \"name\": \"cabbage\", \"quantity\": 1}, {\"id\": 11, \"name\": \"avocado\", \"quantity\": 1}, {\"id\": 8, \"name\": \"bacon\", \"quantity\": 1}, {\"id\": 9, \"name\": \"oranges\", \"quantity\": 1}]}]"

2) curl --request POST -d '{"contents": [{"id":1,"name":"cucumbers","quantity":20},{"id":2,"name":"tomatoes","quantity":2}]}' -H 'Content-Type: application/json' '129.215.216.19:5000/placeOrder?individual_id=42&dateTime=1987-02-04_21:13:49'
Returns order_id

3) curl --request POST -d '{"contents": [{"id":1,"name":"cucumbers","quantity":200},{"id":2,"name":"tomatoes","quantity":2}]}' -H 'Content-Type: application/json' '129.215.216.19:5000/editOrder?order_id=34&dateTime=1987-02-04_21:13:49'
Returns True or False

4) curl '129.215.216.19:5000/requestStatus?order_id=34'
Returns status integer or -1 if order not found

5) curl '129.215.216.19:5000/registerCateringCompany?business_name=catering1&postcode=eh0111'
Returns: registered new / already registered

6) curl '129.215.216.19:5000/cancelOrder?order_id=34'
Returns: true or false

7)  curl '129.215.216.19:5000/registerSupermarket?business_name=catering1&postcode=eh0111'
Returns: registered new / already registered

8) curl '129.215.216.19:5000/updateOrderStatus?order_id=42&newStatus=2'
Returns: True or False
