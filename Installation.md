## Installation

1. Open your terminal and enter the following commands.
   ```
   https://github.com/tanasatit/ku-polls.git
   ```
2. Route to repository.
   ```
   cd ku-polls
   ```

3. Install virtual environment (If you haven't already.).
   ```
   pip install virtualenv
   ```
4. Create a virtual env.
   ```
   python -m venv venv
   ```
5. Activate venv.
   
   for MacOS and Linux
   ```
   source venv/bin/activate
   ```
   for Windows
   ```
   env\Scripts\activate
   ```
6. Install the required packages.
   ```
   pip3 install -r requirements.txt
   ```
7. Create the .env by copying the sample.env

   for Linux or MacOS
   ```
   cp sample.env .env
   ```
   for Windows:
   ```
   copy sample.env .env
   ```
8. Migrate settings and data tables.
   ```
   python manage.py migrate
   ```
9. Load polls data.
   ```
   python manage.py loaddata data/polls-v4.json data/users.json
   ```
10. Run the server.
    ```
    python manage.py runserver
    ```
