"""analysis.py - demo placeholder
Simple analysis function used for tests.
"""

def analyze(data):
    """Return a simple summary of provided iterable data."""
    return {
        "count": len(data),
        "first": data[0] if data else None,
        "last": data[-1] if data else None,
    }

if __name__ == "__main__":
    print(analyze([1,2,3]))
