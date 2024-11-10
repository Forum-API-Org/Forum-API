# Forum-API

![alt text](https://files.oaiusercontent.com/file-8YxFU8SmFaLfD45Ixhk5rhd5?se=2024-11-10T15%3A04%3A44Z&sp=r&sv=2024-08-04&sr=b&rscc=max-age%3D604800%2C%20immutable%2C%20private&rscd=attachment%3B%20filename%3Dc38cb482-a24a-4ff5-9d42-59e3b4c243af.webp&sig=Y%2BOUw%2BJl4hsQho1StjI6Fx50TAWbgEo6yM2fDGAyhsc%3D)

```markdown
# Forum API

This project is a Forum API built with FastAPI. It provides endpoints for user management, category management, topic management, message management, reply management, and voting. The API is designed to be used by administrators and users to manage forum content and interactions.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
  - [User Management](#user-management)
  - [Category Management](#category-management)
  - [Topic Management](#topic-management)
  - [Message Management](#message-management)
  - [Reply Management](#reply-management)
  - [Voting](#voting)
- [Running Tests](#running-tests)
- [License](#license)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/forum-api.git
cd forum-api
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

Create a `.env` file in the root directory of the project and add the following environment

 variables

:

```env
JWT_SECRET_KEY=your_secret_key
DATABASE_URL=your_database_url
```

## Usage

1. Start the FastAPI server:

```bash
uvicorn main:app --reload
```

2. The API will be available at `http://127.0.0.1:8000`.

## API Endpoints

### User Management

- **Get All Users**
  - **URL:** `/users`
  - **Method:** `GET`
  - **Headers:** `Authorization: Bearer <JWT_TOKEN>`
  - **Description:** Retrieves a list of all users. Only accessible by admins.
  - **Response:**
    - `200 OK`: List of `UserResponse` objects.

- **Register User**
  - **URL:** `/`
  - **Method:** `POST`
  - **Body:**
    ```json
    {
      "email": "test@example.com",
      "username": "testuser",
      "password": "password123",
      "first_name": "Test",
      "last_name": "User"
    }
    ```
  - **Description:** Registers a new user with the provided details.
  - **Response:**
    - `201 Created`: The created `User` object.

- **Login User**
  - **URL:** `/login`
  - **Method:** `POST`
  - **Body:**
    ```json
    {
      "username": "testuser",
      "password": "password123"
    }
    ```
  - **Description:** Authenticates a user with the provided login data and returns a JWT token if successful.
  - **Response:**
    - `200 OK`: A dictionary containing the JWT token.

- **Logout User**
  - **URL:** `/logout`
  - **Method:** `POST`
  - **Headers:** `Authorization: Bearer <JWT_TOKEN>`
  - **Description:** Logs out a user by blacklisting the provided JWT token.
  - **Response:**
    - `200 OK`: A message indicating the user has been logged out.

- **Give User Read Access**
  - **URL:** `/read_access`
  - **Method:** `PUT`
  - **Headers:** `Authorization: Bearer <JWT_TOKEN>`
  - **Body:**
    ```json
    {
      "user_id": 1,
      "category_id": 1
    }
    ```
  - **Description:** Grants read access to a user for a specific category. Only accessible by admins.
  - **Response:**
    - `200 OK`: A message indicating the access change, or an error response.

- **Give User Write Access**
  - **URL:** `/write_access`
  - **Method:** `PUT`
  - **Headers:** `Authorization: Bearer <JWT_TOKEN>`
  - **Body:**
    ```json
    {
      "user_id": 1,
      "category_id": 1
    }
    ```
  - **Description:** Grants write access to a user for a specific category. Only accessible by admins.
  - **Response:**
    - `200 OK`: A message indicating the access change, or an error response.

- **Revoke User Access**
  - **URL:** `/revoke_access`
  - **Method:** `DELETE`
  - **Headers:** `Authorization: Bearer <JWT_TOKEN>`
  - **Body:**
    ```json
    {
      "user_id": 1,
      "category_id": 1
    }
    ```
  - **Description:** Revokes access for a user from a specific category. Only accessible by admins.
  - **Response:**
    - `204 No Content`: A message indicating the access revocation, or an error response.

- **View Privileged Users**
  - **URL:** `/privileges`
  - **Method:** `GET`
  - **Headers:** `Authorization: Bearer <JWT_TOKEN>`
  - **Query Parameters:** `category_id`
  - **Description:** Retrieves a list of users with access to a specific category. Only accessible by admins.
  - **Response:**
    - `200 OK`: List of `UserAccessResponse` objects.

### Category Management

- **Get All Categories**
  - **URL:** `/categories`
  - **Method:** `GET`
  - **Headers:** `Authorization`
  - **Description:** Retrieves a list of all categories.
  - **Response:**
    - `200 OK`: List of `CategoryResponse` objects.
  
- **Get Category by ID**
  - **URL:** `/categories/{category_id}`
  - **Method:** `GET`
  - **Headers:** `Authorization`
  - **Description:** Retrieves a specific category by ID.
  - **Response:**
    - `200 OK`: The `Category` object.

- 

- **Create Category**
  - **URL:** `/categories`
  - **Method:** `POST`
  - **Headers:** `Authorization`
  - **Body:**
    ```json
    {
      "name": "New Category"
    }
    ```
  - **Description:** Creates a new category with the provided name. Only accessible by `admins`.
  - **Response:**
    - `201 Created`: The created `Category` object.

- **Lock Category**
  - **URL:** `/categories/lock/{category_id}`
  - **Method:** `PUT`
  - **Headers:** `Authorization`
  - **Description:** Locks a category, preventing new topics from being created in it. Only accessible by `admins`.
  - **Response:**
    - `200 OK`: A message indicating the category has been locked.

- **Unlock Category**
  - **URL:** `/categories/unlock/{category_id}`
  - **Method:** `PUT`
  - **Headers:** `Authorization`
  - **Description:** Unlocks a category, allowing new topics to be created in it. Only accessible by `admins`.
  - **Response:**
    - `200 OK`: A message indicating the category has been unlocked.

- **Make Category Private**
  - **URL:** `/categories/private/{category_id}`
  - **Method:** `PUT`
  - **Headers:** `Authorization`
  - **Description:** Makes a category private, requiring users to have access to view and interact with it. Only accessible by `admins`.
  - **Response:**
    - `200 OK`: A message indicating the category has been made private.

- **Make Category Public** 
    - **URL:** `/categories/public/{category_id}`
    - **Method:** `PUT`
    - **Headers:** `Authorization`
    - **Description:** Makes a category public, allowing all users to view and interact with it. Only accessible by `admins`.
    - **Response:**
        - `200 OK`: A message indicating the category has been made public.

### Topic Management

- **Get All Topics**
    - **URL:** `/topics`
    - **Method:** `GET`
    - **Headers:** `Authorization`
    - **Query Parameters:** `search`, `sort_by`, `sort_order`, `limit`, `offset`
    - **Description:** Retrieves a list of all topics. Topics from private categories require the user to have read access for this category. Admins can view all topics. The `search` parameter filters topics by name. The `sort_by` parameter specifies the field to sort by (e.g., `topic_date`). The `sort_order` parameter specifies the sort order (`asc` or `desc`). The `limit` and `offset` parameters are used for pagination.
    - **Response:**
        - `200 OK`: List of `TopicResponse` objects.

- **Get Topic by ID** 
  - **URL:** `/topics/{topic_id}`
  - **Method:** `GET`
  - **Headers:** `Authorization`
  - **Description:** Retrieves a specific topic by ID. Topics from private categories require the user to have read access for this category. Admins can view all topics.
  - **Response:**
    - `200 OK`: The `Topic` object.

- **Create Topic**
  - **URL:** `/topics`
  - **Method:** `POST`
  - **Headers:** `Authorization`
  - **Body:**
    ```json
    {
      "name": "New Topic",
      "category_id": 1
    }
    ```
  - **Description:** Creates a new topic with the provided details. Every user can create a topic in a public category. Only admins and users with write access can create topics in private categories.
  - **Response:**
    - `201 Created`: The created `Topic` object.

- **Lock Topic** 
  - **URL:** `/topics/lock/{topic_id}`
  - **Method:** `PUT`
  - **Headers:** `Authorization`
  - **Description:** Locks a topic, preventing new replies from being added to it. Only accessible by `admins`.
  - **Response:**
    - `200 OK`: A message indicating the topic has been locked.

- **Unlock Topic** 
  - **URL:** `/topics/unlock/{topic_id}`
  - **Method:** `PUT`
  - **Headers:** `Authorization`
  - **Description:** Unlocks a topic, allowing new replies to be added to it. Only accessible by `admins`.
  - **Response:**
    - `200 OK`: A message indicating the topic has been unlocked.

- **Choose Best Reply**
  - **URL:** `/topics/best_reply/{topic_id}`
  - **Method:** `PUT`
  - **Headers:** `Authorization`
  - **Description:** Marks a reply as the best reply for a topic. Only accessible by the `topic owner`.
  - **Response:**
    - `200 OK`: A message indicating the best reply has been chosen.

### Message Management

- **Get Conversation**
  - **URL:** `/messages`
  - **Method:** `GET`
  - **Description:** Retrieves a list of all messages with a user.
  - **Response:**
    - `200 OK`: List of `MessageResponse` objects.

- **Create Message**
  - **URL:** `/messages`
  - **Method:** `POST`
  - **Body:**
    ```json
    {
      "text": "Content of the new message",
      "receiver_id": 1
    }
    ```
  - **Description:** Creates a new message with the provided details.
  - **Response:**
    - `201 Created`: The created `Message` object.

- **Get Conversaions**
  - **URL:** `/messages`
  - **Method:** `GET`
  - **Description:** Retrieves a list of conversations of the user.
  - **Response:**
    - `200 OK`: List of `MessageResponse` objects.
### Reply Management

- **Create Reply**
  - **URL:** `/replies`
  - **Method:** `POST`
  - **Body:**
    ```json
    {
      "text": "Content of the new reply",
      "topic_id": 1
    }
    ```
  - **Description:** Creates a new reply with the provided details to a topic.
  - **Response:**
    - `201 Created`: The created `Reply` object.

### Voting

- **Vote on Reply**
  - **URL:** `/votes/topic`
  - **Method:** `POST`
  - **Body:**
    ```json
    {
      "reply_id": 1,
      "vote": "upvote"
    }
    ```
  - **Description:** Casts a vote on a reply.
  - **Response:**
    - `200 OK`: A message indicating the vote was successful.

## Running Tests

1. Install the test dependencies:

```bash
pip install -r requirements-test.txt
```

2. Run the tests:

```bash
pytest
```

## License

This project is licensed under the MIT License. See the LICENSE file for details.
```

This `README.md` file provides a general overview of the project, installation instructions, usage details, API endpoints, and information on running tests. Adjust the content as needed to fit your specific project details.This `README.md` file provides a general overview of the project, installation instructions, usage details, API endpoints, and information on running tests. Adjust the content as needed to fit your specific project details.