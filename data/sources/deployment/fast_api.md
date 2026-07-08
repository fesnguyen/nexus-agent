# FastAPI --- Quick Mental Model

> Goal: Understand **what FastAPI is**, **why it exists**, and **how to
> use it** without getting lost.

------------------------------------------------------------------------

# One Sentence

**FastAPI is a framework for turning Python functions into web APIs.**

Instead of writing low-level networking code, you describe your
endpoints as Python functions.

------------------------------------------------------------------------

# Mental Model

Imagine your AI application as a restaurant.

    Client
       │
    HTTP Request
       │
       ▼
    FastAPI
       │
    Chooses the correct endpoint
       │
    Runs your Python function
       │
    Returns JSON
       ▼
    Client

FastAPI is the **receptionist**.

It doesn't do the business logic.

It simply:

-   receives requests
-   validates input
-   calls your function
-   sends back the response

------------------------------------------------------------------------

# Why FastAPI?

Without FastAPI:

-   Parse HTTP yourself
-   Read JSON yourself
-   Validate data yourself
-   Handle errors yourself
-   Build API documentation yourself

With FastAPI:

``` python
@app.get("/hello")
def hello():
    return {"message": "Hello"}
```

Done.

------------------------------------------------------------------------

# Everything is an Endpoint

Think of an endpoint as a **public function** that anyone can call over
the network.

Example:

    GET /hello

calls

``` python
def hello():
```

------------------------------------------------------------------------

# Request → Function → Response

Every API follows this pattern.

    Request
          │
          ▼
    Python Function
          │
          ▼
    Response

Example

Client sends

    GET /users/3

FastAPI runs

``` python
def get_user(id=3):
```

Returns

``` json
{
  "id":3,
  "name":"Alice"
}
```

------------------------------------------------------------------------

# The FastAPI Object

``` python
app = FastAPI()
```

Think of it as your **web server configuration**.

Every endpoint attaches to this object.

    app
     ├── /chat
     ├── /login
     ├── /health
     └── /search

------------------------------------------------------------------------

# HTTP Methods

Different actions use different verbs.

  Method   Meaning
  -------- -------------
  GET      Read
  POST     Create
  PUT      Replace
  PATCH    Update part
  DELETE   Remove

Example

``` python
@app.post("/chat")
```

means

> Someone wants to create a chat request.

------------------------------------------------------------------------

# Path Parameters

    GET /users/42

``` python
@app.get("/users/{id}")
def get_user(id:int):
    ...
```

FastAPI automatically converts `"42"` into an integer.

------------------------------------------------------------------------

# Query Parameters

    GET /search?q=python&page=2

becomes

``` python
def search(q:str, page:int=1):
```

------------------------------------------------------------------------

# Request Body

Sometimes the client sends JSON.

    POST /chat

``` json
{
    "message":"Hello"
}
```

FastAPI converts it into a Python object.

------------------------------------------------------------------------

# Pydantic

FastAPI uses **Pydantic** to describe data.

``` python
class ChatRequest(BaseModel):
    message: str
```

Now FastAPI automatically

-   validates input
-   converts types
-   reports errors clearly
-   generates documentation

You don't manually inspect JSON.

------------------------------------------------------------------------

# Dependency Injection

Sometimes many endpoints need the same object.

Example:

-   database
-   AI model
-   configuration
-   authentication

Instead of creating them every request,

FastAPI can inject them.

Mental model:

    Endpoint
         │
         ▼
    Needs Database
         │
    FastAPI provides it

------------------------------------------------------------------------

# Async

Many APIs spend time waiting.

Examples

-   database
-   internet
-   LLM inference
-   file reading

Instead of blocking,

``` python
async def chat():
```

lets other requests run while waiting.

Think of a chef cooking multiple dishes instead of staring at boiling
water.

------------------------------------------------------------------------

# Automatic Documentation

Start the server.

Visit

    /docs

You instantly get interactive API documentation.

No extra work.

------------------------------------------------------------------------

# Typical AI Backend

    Browser
        │
     POST /chat
        │
    FastAPI
        │
    Agent
        │
    LLM
        │
    Tools
        │
    RAG

FastAPI only handles communication.

Your AI logic stays separate.

------------------------------------------------------------------------

# Minimal Example

``` python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello"}

@app.get("/square/{x}")
def square(x:int):
    return {"result": x*x}
```

Run

``` bash
fastapi dev main.py
```

or

``` bash
uvicorn main:app --reload
```

Open

    http://127.0.0.1:8000/docs

------------------------------------------------------------------------

# Why AI Projects Love FastAPI

It is:

-   Easy to learn
-   Very fast
-   Automatic validation
-   Automatic documentation
-   Excellent async support
-   Works naturally with Python ML libraries
-   Easy to deploy
-   Clean architecture for separating API from AI logic

------------------------------------------------------------------------

# Keep This Mental Picture

    Internet
         │
         ▼
     FastAPI
         │
    Routing
    Validation
    Documentation
         │
    Calls
    Your Python Code
         │
    Business Logic
         │
    Returns JSON

**FastAPI is not your AI.**

It is the **bridge between the outside world and your Python code**.
