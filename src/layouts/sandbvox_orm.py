import peewee as pw

# Define your database
db = pw.SqliteDatabase('your_database.db')

# Define your model(s)
class BaseModel(pw.Model):
    class Meta:
        database = db

class YourTable(BaseModel):
    field1 = pw.CharField()
    field2 = pw.IntegerField()
    # Add as many fields as your table has

# Connect to the database
db.connect()

# Query the database
query = YourTable.select()