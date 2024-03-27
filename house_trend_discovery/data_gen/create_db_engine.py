from sqlalchemy import create_engine, URL, text

url_object = URL.create(
    "postgresql",
    username="trends",
    password="example",
    host="localhost",
    database="trends",
)

engine = create_engine(url_object, echo=True)
