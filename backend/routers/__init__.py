"""HTTP routes. One module per feature, all wired up in main.py.

A route's job is small: read the request, call queries/, turn the result
into a response model, raise HTTPException on anything bad. No SQL in here.
"""
