# Locations-API
API:

The API allows to record location data of entered IP addresses. It has registration and authentication functions using JWT. It was created in the Flask framework. It can be found at the link: 

https://api-sofomo.herokuapp.com/,

Manual operation:
1. To register, you need to send a POST request to https://api-sofomo.herokuapp.com/signup , containing JSON in the body with login data ({"login": "...", "password": "..."}). For this, use an application that allows you to manually send HTTP requests (such as Postman).
2. After creating a user, to log in, send a GET request to https://api-sofomo.herokuapp.com/login, using the previously entered login and password as authorization data in Postman. The response will send a token, which should be copied and pasted into the header, adding a new line named "x-access-token". That is, {"x-access-token": "<copy token>"}. Use the given header every time we send a query that requires being logged in.
3. To get a list of locations stored in the database, send a GET query to https://api-sofomo.herokuapp.com/location . Remember the token header.
4. To add a location, send a POST query to https://api-sofomo.herokuapp.com/location/<ip> , where ip is the ip address of the device, the location of which we want to save. Note: as the number of queries in the free version of ipstack is limited, so this function should be used sparingly.
5. To remove a location from the database, send a DELETE query to https://api-sofomo.herokuapp.com/location/<id>, where id is the unique identification number of the record in the database.
