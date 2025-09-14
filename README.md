# MyBlog
### Video Demo: https://youtu.be/AfFE7ygUKRE
#### Description:
This project is a dynamic **CRUD-based** blog website. Users can create & delete their blog posts, customize their profile, follow or unfollow others and search for other users. The aim was to create a simple yet complete web application that demonstrates understanding of backend logic, templating engines, routing, user authentication, and frontend design.

## Features
- User Authentication
- Create and Delete Blog Posts
- Customizable Profile
- Follow/Unfollow Other Users
- Search Functionality
- Pagination
- Responsive Design
- SQLite Database Integration

 ## Tech Stack
 - **Frontend:** HTML, CSS, Bootstrap, Jinja
 - **Backend:** Flask (Python)
 - **Database:** SQLite

## File Structure

### app.py
This is the main Flask application that handles routing, request handling, database connection, and rendering templates. All user input is validated and managed securely with session cookies. It also uses **CSRF tokens** to secure the user from CSRF attacks. It contains the following routes:
- `/` : home page from where the user can post blogs and view their feed
- `/login` : login page that does user authentication
- `/logout` : logs out the user
- `/register` : register page that creates new accounts
- `/explore` : explore page displaying all the posts posted by every user
- `/profile/<username>` : profile page containing a user's profile details and posts
- `/search` : searches for users
- `/delete` : deletes a post
- `/follow/<username>` : follows/unfollows a user

---

### helper.py
This Python file contains a few helper functions that are imported by **app.py**. Helper functions include:
- `apology()`: returns an apology page with a cat image when an error occurs
- `get_db()` : establishes a connection with the database
- `login_required()` : a wrapper function that checks for session cookie
- `pfp_check()` : used to handle invalid request for user pfp
- `time_ago()` : converts a timestamp into a more readable format

---

### config.py
This Python file configures a few environment variables

---

### requirements.txt
This text file contains the list of external libraries used. It includes:
- Flask
- Flask-Wtf
- Flask-Session

---

### blog.db
This is the database that contains three tables:
- `users` : contains user data
- `posts` : contains information about every post
- `follows` : maintains the relationship between followers and followees

Below is the schema definition of each table:
```
CREATE TABLE users (
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE NOT NULL,
hash TEXT NOT NULL,
name TEXT,
bio TEXT,
pfp TEXT);

CREATE TABLE posts (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER NOT NULL,
content TEXT NOT NULL,
post_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE);

CREATE TABLE follows (
follower_id INTEGER NOT NULL,
follows_id INTEGER NOT NULL,
PRIMARY KEY (follower_id, follows_id),
FOREIGN KEY (follower_id) REFERENCES users(id) ON DELETE CASCADE,
FOREIGN KEY (follows_id) REFERENCES users(id) ON DELETE CASCADE
);
```

---

### `static/`
This directory contains `styles.css` and another directory called `images/` which contains the avatar images.

---

### `templates/`
This contains the Jinja HTML templates and here is the list of templates:
- `layout.html` : defines the structure of the entire web app and every other major template extends it
- `nav.html` : contains the navigation bar and is included in `layout.html`
- `login.html` : login page that displays the login form
- `register.html` : allows the user to register for a new account via the register form
- `index.html` : home page which displays the feed as well as the post submission form through which new posts can be posted
- `explore.html` : displays all the posts posted by all the users
- `profile.html` : profile page that displays user data and their posts
- `search.html` : displays search results
- `posts.html` : a template that is included anywhere posts need to be displayed in a table format
- `apology.html` : displays an error message in case of a 404, 400 or 500 error

---

## Design Decisions & Trade Offs
### Templating
 I didn't use the `posts.html` template to display search results despite requiring a very similar table structure because it doesn't display posts. This results in a small amount of repeated code. `posts.html` also combines the table and pagination which is another reason for this issue. Since this is a very small project, I didn't mind it but I will definitely keep in mind to not copy paste code.

### CSS
`styles.css` was mostly written by ChatGPT. I would like to mention that this is the only place where I have used AI to generate code because styling didn't feel like coding and I was too invested in implementing the backend logic. I still added a few of my own changes to the CSS at the end so it's not completely made by AI.

### Database
I wanted to add a `DEFAULT` constraint (after creating the table) for the `pfp` column from `users` table but I couldn't alter the constraints of the table because of the limitations of sqlite. In the future I am thinking about switching to Postgres or MYSQL because they are scalable too. But since this was a very small scale project, I was okay with it.

### CSRF Protection
I didn't know how to add CSRF protection to the logout route and this is the only unresolved backend issue in this application. It isn't technically a security problem because the user's data will be safe but I hope to learn how to fix this issue in the future. Other major forms are csrf protected though.

### User Authentication
I initially planned on using the Flask-Login library but since the login mechanics were pretty simple, I decided to manually deal with session cookies. It increases the lines of code but it is something that was fundamentally simple so I decided to implement it manually instead of using a third party library to solve the problem.

### Routing
I have used the same route for following or unfollowing someone because the authentication logic was very similar. The name `/follow/<username>` might be a little misleading but I couldn't think of another name that represents both functionality.
