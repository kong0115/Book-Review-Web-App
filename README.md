# Project 1

Web Programming with Python and JavaScript

This is a book review web application. Users are directed to the login page when they visit the website. Users must sign up for the website for the first time and then log in to the website before using the application. Once users have logged in, they are directed to the home page where they can use the search box in the navigation bar on the top to search for books in the database. After users click on the search button, it will return a list of matching results or an error message if nothing found.

Users are directed to a book page when they click on the book from the list of matching results. There are 4 different sections on the book page. The top left section displays the details of the book which includes the title, author, publication year, and ISBN of the book.
The top right section displays the average rating and reviews count from Goodreads, another book review website. The middle section displays reviews made by users for the book. The bottom section is the place where users can submit a review that consists of rating (on a scale of 1 to 5)and text. Users can only submit at most one review for the same book.

Users can also query for book details and reviews data received from Goodreads using the website's API through /api/isbn/<isbn> route. The API will return the book data in the format of the JSON response. Users will be able to log out of the website by clicking the log out button under the dropdown list located on the top right corner of the page. Once users have logged out, their sessions are cleared, and they will be redirected to the login page.
