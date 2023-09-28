# internship-Meduzzen
Repository of my internship in Meduzzen.

---
<h1> How to start? </h1>

1. Clone the Repository:
git clone https://github.com/AlllLiIIINa/internship-Meduzzen.git
2. Install Dependencies:
- cd internship-Meduzzen 
- python -m venv venv
- source venv/bin/activate  (On Windows, use venv\Scripts\activate)

3. Install python modules:
pip install -r requirements.txt

---
<h1> How to run? </h1>
To run the Application:
uvicorn app.main:app --reload

---
<h1> How to run the application within  Docker </h1>

1. Build the Docker image:
docker build -t internship-meduzzen-app .
2. Start the Docker container:
docker run -p 8000:8000 internship-meduzzen-app
3. The application will now be accessible at http://localhost:8000 in your web browser.

---
<h1> How to run the application tests within Docker </h1>

1. Build the Docker image for tests:
docker build -t internship-meduzzen-tests -f Dockerfile.tests .
2. Run the tests using the Docker container:
docker run internship-meduzzen-tests

---
<h1> How to make and apply migrations </h1>

1. Create a migration:
alembic revision --autogenerate -m "YOURMIGRATIONNAME"
2. Apply the migration:
alembic upgrade head
