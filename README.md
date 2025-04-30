# Agile Web Development Group Project (CITS3403) - CGTools

[ENTER DESCRIPTION HERE]

## Group Members

| **UWA ID** | **Name**   | **GitHub Username** |
|------------|------------|---------------------|
| 23390625      | Cameron Hart    | camhart21  |
| 23214051      | Harry Chan      | Crypteemo  |
| 23245495      | Jordy Kappella  | OgmaLogic  |
| 22957489      | Nick Nasiri     | schain-dev |


## Setup and Installation

1. **Create and activate a virtual environment:**

    ```
    # Create venv
    python3 -m venv venv

    # Activate venv
    source venv/bin/activate        # Mac/Linux
    .\venv\Scripts\activate          # Windows
    ```

2. **Install dependencies:**

    ```
    pip install -r requirements.txt
    ```

3. **Run the Flask server:**

    ```
    export FLASK_APP=app
    export FLASK_ENV=development
    flask run --debug
    ```

    _(On Windows CMD use `set FLASK_APP=app` instead.)_

4. **Access the app:**

    Open your browser and go to:

    ```
    http://localhost:5000
    ```