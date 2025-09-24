from datetime import datetime, date
from sqlalchemy.inspection import inspect

# -------------------------------------------------

def to_dict(obj, seen=None):
    """
    Recursively convert SQLAlchemy models, dataclasses, and other Python objects to JSON-safe dicts.
    Prevents infinite recursion with cyclic references.
    """
    if seen is None:
        seen = set()

    # Prevent cyclic references
    if id(obj) in seen:
        return None
    seen.add(id(obj))

    # Simple types
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj

    # Dates → ISO format
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    # List / Tuple → Recursively serialize items
    if isinstance(obj, (list, tuple, set)):
        return [to_dict(item, seen) for item in obj]

    # Dict → Recursively serialize values
    if isinstance(obj, dict):
        return {k: to_dict(v, seen) for k, v in obj.items()}

    # SQLAlchemy model
    try:
        mapper = inspect(obj)
        data = {}
        for column in mapper.attrs:
            value = getattr(obj, column.key)
            data[column.key] = to_dict(value, seen)
        return data
    except Exception:
        pass

    # Dataclass
    try:
        from dataclasses import asdict, is_dataclass
        if is_dataclass(obj):
            return {k: to_dict(v, seen) for k, v in asdict(obj).items()}
    except ImportError:
        pass

    # Has to_dict method
    if hasattr(obj, "to_dict") and callable(obj.to_dict):
        return to_dict(obj.to_dict(), seen)

    # Fallback to __dict__ for plain objects
    if hasattr(obj, "__dict__"):
        return {k: to_dict(v, seen) for k, v in vars(obj).items() if not k.startswith("_")}

    # Final fallback: Stringify
    return str(obj)