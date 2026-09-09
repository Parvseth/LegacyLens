import os
import tempfile
from app.services.parsers.python_parser import PythonParser
from app.services.parsers.java_parser import JavaParser
from app.services.analysis_service import detect_duplicates, detect_circular_deps


def test_python_parser():
    code = """
import os
import sys

class DataProcessor:
    def process_data(self, item):
        if item > 0:
            for i in range(item):
                if i % 2 == 0:
                    print(i)
        return item
"""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code)
        temp_path = f.name

    try:
        parser = PythonParser()
        fv = parser.parse(temp_path, os.path.dirname(temp_path))
        assert fv.loc > 0
        assert fv.num_classes == 1
        assert fv.num_functions == 1
        assert fv.import_count == 2
        assert fv.cyclomatic_complexity > 1.0
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_circular_dependency_algorithm():
    # Graph: A -> B -> C -> A (cycle), and D -> E (no cycle)
    edges = {
        "A.py": ["B.py"],
        "B.py": ["C.py"],
        "C.py": ["A.py"],
        "D.py": ["E.py"],
        "E.py": [],
    }
    cycles = detect_circular_deps(edges)
    assert "A.py" in cycles
    assert "B.py" in cycles
    assert "C.py" in cycles
    assert "D.py" not in cycles
    assert "E.py" not in cycles
