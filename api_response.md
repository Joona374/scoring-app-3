# Standard API Response Structure Reminder

#### For successful operations that return data

```python
return response_schema_object  # Direct return
```

#### For successful operations that don't return meaningful data:

```python
return {"message": "Operation completed successfully"} # Direct return
```

#### For errors:

```python
raise HTTPException(status_code=400, detail="Specific error message") # Raise an HTTPException with a specific error message
```
