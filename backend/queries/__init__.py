"""All the SQL lives in here, one module per group of tables.

Rules:
  - every function takes the connection as its first argument
  - NEVER f-string a value into SQL. always pass params:
        await cur.execute("select * from users where id = %s", (user_id,))
    the second one is a tuple, the trailing comma matters
  - routes call these, these don't call routes
"""
