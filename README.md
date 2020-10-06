# ANNA_test

This is a test project for a company called ANNA. It's a web API + server for a personal task manager.
Run “ANNA_test_server.py” to start the server.
Functionality:
- Users can register and login using username + password, and they receive a JSON web token after for authentication. The system can have multiple users. The user receives a token the moment they register or login, they can stay in the system for 30 days, each successful login sends them a new token, prolonging their stay in the system. The system stores passwords without any hashing (for now).
- The client communicates with the server using http headers and JSONs. The token is transferred in the header “Token”.
- The database in on SQLite. There are 2 tables: “users” and “tasks”. The structures are following:
            CREATE TABLE IF NOT EXISTS users (
            username text PRIMARY KEY NOT NULL,
            password text NOT NULL
            );

            CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username text,
            name text NOT NULL,
            description text NOT NULL,
            creation_time text NOT NULL,
            status text NOT NULL CHECK(status in ('new', 'planned', 'working', 'finished')),
            planned_end_time text,
            FOREIGN KEY(username) REFERENCES users(username)
            );
- Users can create, edit (but not the creation time), and delete their tasks. Tasks have IDs inaccessible by users (but accessible by their clients), this means that there can exist tasks having same names and other attributes (but not IDs).
- Users can get all their tasks or filter tasks by attributes other than ID.
- A user cannot access another user’s data because their username is within their token: whoever has the token is the user.
- Logging out happens on the client side by “forgetting” the token.
