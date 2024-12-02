# Points Management REST API



This is a Flask-based REST API for managing user points transactions. It allows you to:

- Add points with a payer and timestamp.
- Spend points using FIFO rules while ensuring no payer's balance goes negative.
- Retrieve the current point balances per payer.



## Requirements

- Python 3.8+

- `pip` (Python package manager)

- SQLite (comes pre-installed with Python)



## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Jerry2423/points_management_api.git
cd points_management_api
```

### 2. Set Up a Python Virtual Environment

To ensure dependencies are isolated, use a virtual environment:

```bash
python3 -m venv points_env
source points_env/bin/activate  # On Windows: points_env\Scripts\activate
```

### 3. Install Dependencies

Install the required Python libraries using `pip`:

```bash
pip install -r requirements.txt
```

### 4. Set Up the Database

Initialize or reset the SQLite database:

- To create and initialize the database:

  ```bash
  python3 init_db.py
  ```

- To reset and clean the database:

  ```bash
  python3 clean_db.py
  ```

### 5. Run the Application

Start the Flask development server:

```bash
python3 app.py
```

The application allows customization of rate-limiting settings through command-line arguments using the Token Bucket Algorithm. Below are the available options:

1. `--rate_limit`:

   1. Defines the number of requests allowed per second.
   2. Default value: `5`.

2. `--capacity`:

   1. Specifies the maximum burst capacity of requests allowed.
   2. Default value: `10`.

3. Example Usage:

   1. To run the application with a custom rate limit of 10 requests per second and a capacity of 20 requests: 

      ```bash
      python3 app.py --rate_limit 10 --capacity 20
      ```

### 6. Testing the API

You can use tools like [Postman](https://www.postman.com/) or `curl` to test the endpoints.

#### Example Transactions 

1. **Add Points** Call the `/add` endpoint with the following transactions (each line is a separate call):   

   1. ```bash
      curl -X POST -H "Content-Type: application/json" -d '{
           "payer": "DANNON",
           "points": 300,
           "timestamp": "2022-10-31T10:00:00Z"
         }' http://localhost:8000/add
      ```

   2. ```bash
      curl -X POST -H "Content-Type: application/json" -d '{
           "payer": "UNILEVER",
           "points": 200,
           "timestamp": "2022-10-31T11:00:00Z"
         }' http://localhost:8000/add
      ```

   3. ```bash
      curl -X POST -H "Content-Type: application/json" -d '{
           "payer": "DANNON",
           "points": -200,
           "timestamp": "2022-10-31T15:00:00Z"
         }' http://localhost:8000/add
      ```

   4. ```bash
      curl -X POST -H "Content-Type: application/json" -d '{
           "payer": "MILLER COORS",
           "points": 10000,
           "timestamp": "2022-11-01T14:00:00Z"
         }' http://localhost:8000/add
      ```

   5. ```bash
      curl -X POST -H "Content-Type: application/json" -d '{
           "payer": "DANNON",
           "points": 1000,
           "timestamp": "2022-11-02T14:00:00Z"
         }' http://localhost:8000/add
      ```

2. **Spend Points** 

   1. Call the `/spend` endpoint with the following request:

      ```bash
      curl -X POST -H "Content-Type: application/json" -d '{
        "points": 5000
      }' http://localhost:8000/spend
      ```

   2. **Expected Response**:

      ```js
      [
        { "payer": "DANNON", "points": -100 },
        { "payer": "UNILEVER", "points": -200 },
        { "payer": "MILLER COORS", "points": -4,700 }
      ]
      ```

3. **Check Balance**

   1. Call the `/balance` endpoint:

      ```bash
      curl http://localhost:8000/balance
      ```

   2. **Expected Response**:

      ```js
      {
        "DANNON": 1000,
        "UNILEVER": 0,
        "MILLER COORS": 5300
      }
      ```