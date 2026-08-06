api: Waiter
It takes the order from the customer (react app) to the kitchen (/core) and then returns with the food. 

- main.py: Starts up the whole FastAPI application. Create one single Bank object (backed by one SQLiteStorage) that every request will share. Setup CORS so your react frontend app running on a different adress allowed to talk to it. 

- auth.py: Handles the login ticket. When you login successfully, this file creates a JWT token (a signed piece of text that that proves yes this is really user 07 and it expires every 24 hours). Everytime you make a request that needs you to be looged in this, this file checks that the ticket is real and not expired and then figures out to which user it belongs to.

- schema.py: Defines the shape of data. This file is a blueprint build by pydantic that FastAPI use to automatically check "did you send me the right kind of data? ". 

- routes: The actual doors the customer can knock on. 
    - account.py: Contains /signup , /login , /me , /deposit , /withdraw , /transfer , /history. Each one is a small function that takes the request, calls the appropriate method in Bank, and then returns the response.

    - assistant.py: The door for talking to the ai. Contains /assistant (in which we send a message and get a   reply) and /assistant/confirm which actually executes the proposed transaction after the human say yes. 

    - transactions.py: 

    - __init__.py: Converts the folder into package that can be imported. 





QUESTIONS: 
How does the file figures out JWT token belongs to which user?
What are routes and routers in FastAPI? 



API: A deiende way for two pieces of software to connect to each other. React app doesn't know about python and python doesn't run in the browser. So the API is the aggred upon language between them. Most modern API's send data back and forth in the format of JSON. 
REST API: A common style API where you sue URL and a verb to describe an action. GET /me means give me info. POST /deposit means that create or do a deposit action. 
Endpoints: One specific url that do one specific job. /login , /transfer , /signup are all endpoints. These enpoints are in the account and assistant files. 
HTTP Methods: GET means "just give me the information, don't change anything". POST means "I am sending you data please do something with it".
CORS (Cross Origin Resource Sharing): Browsers block a web-page from one adress (localhost:5173) from talking to a server at a different adress (localhost:8000) as a security measure. CORS is the backend explicitly saying "I trust requests coming from localhost:5173". 
Middleware: Code that runs on every sigle request before it reaches your actual route function. CORS is a middleware. Every request passes through it first. 
JWT (JSON Web Token): A signed piece of text that proves your identity for a period of time, without the server being needing to remember you. 

FastAPI specific terms:
Pydantic: A python class that defines exactly what shape of data is required and automatically checks incoming data against that shape, rejecting anything that doesn't match. 
Dependency Injection (Depends): A FastAPI feature in which a route function says before you run me. run that function and hand me the result. 