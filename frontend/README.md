frontend: What the human actually sees.

- src: 
    - api.js: The messenger. Everytime the react app needs to talk to the backend, it goes thorugh here. It knows the ackend adress and ataches JWT Token to every request so you don't have to do it yourself. 

    - main.jsx: The map. It decides "if the browser shows /login diplay the login page. If the browser shows /dashboard show the dashboard page". 

    - pages: Contain one file per screen. Each is a small program that waits for you to click something and then calls api.js to do something. The .jsx files in it are also called components. 



QUESTIONS: 
When applying styling through CSS will it be done in jsx files in pages? 

JSX: One way of writing the HTML like code directly into javascript. This code is converted to javasvript before runing. 
Vite: The tool that runs your react app during development and eventually bundles it into real files the browser can load. It is fast because it don't rebuild the whole app every time you save, it only rebuilds the piece that changed. 
