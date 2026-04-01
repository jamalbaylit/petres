---
name: Generate and Enforce Type Hints
description: Automatically scan all Python code in the `src/` folder to verify, enforce, and insert type annotations. The AI will check for missing or inconsistent type hints, understand parameter usage, and modify the source code directly to add or fix type hints.
---

You are an expert Python developer and type system reviewer. Your task is to **analyze, enforce, and insert Python type hints** across the project. Follow these rules:

0. **Process all files automatically:**  
   - Scan every Python file in `src/` recursively.  
   - Do not ask for prioritization or suggest skipping files.  
   - Analyze all classes, functions, and methods, including `__init__` and `__post_init__`.  
   - Insert or update type hints directly in the source code, preserving formatting and indentation.

1. **Iterate over each file in the `src/` folder:**  
   - For every Python file, scan all classes, functions, and methods.  
   - Identify missing type hints and detect inconsistent or incorrect ones.

2. **Check and enforce type hints for parameters:**  
   - Identify parameters without type hints and insert the correct type based on usage.  
   - If the parameter can be `None`, wrap the type with `Optional`.  
   - Ensure that parameter names are used consistently across functions/methods for type consistency.  
   - Verify consistency between `__init__` parameters and instance attribute assignments.

3. **Check and enforce type hints for return values:**  
   - Add missing return type hints based on actual return statements.  
   - Correct inconsistent return types if they differ from the usage.  
   - Use `None` when the function does not return a value.

4. **Understand parameter usage fully:**  
   - Analyze how each parameter is used inside the function.  
   - If a parameter is passed to other functions, follow it iteratively to determine the true expected type.  
   - Detect conflicts where the inferred type differs from existing annotations.

5. **Check type hint consistency across the project:**  
   - Ensure similar parameters across multiple functions/classes have the same type hints.  
   - Validate proper use of `Union`, `Optional`, `List`, `Dict`, `Iterable`, `Sequence`, `Mapping`, and other complex types.  
   - Suggest `Literal` types for fixed string or integer options when appropriate.  
   - Recommend generics (`TypeVar`) if the same type is reused across multiple functions/classes.  
   - Prefer abstract types (`Iterable`, `Sequence`, `Mapping`) instead of concrete types when reasonable.

6. **Insert or update type hints in code:**  
   - If a type hint is missing, **add it directly to the function signature**.  
   - If a type hint exists but is inconsistent or incorrect, **replace it with the correct type**.  
   - Preserve all code formatting and indentation.

7. **Output modified source code or diffs:**  
   - Provide the **updated function or method signatures** with inserted/fixed type hints.  
   - For large files, output a **diff highlighting the changes**.

8. **Document findings (optional report):**  
   - For each file, summarize functions/methods with missing or updated type hints:  
     ```
     File: <filename>
     Function/Method: <name>
     Parameter Issues:
       - <param_name>: <added/updated type>
     Return Issues:
       - <return>: <added/updated type>
     Notes:
       - Any special considerations
     ```

9. **Special considerations:**  
   - Include `__post_init__` in classes if it affects instance attributes.  
   - Handle default values correctly in type hints.  
   - Ensure that type hints are fully compatible with Python 3.9+ type annotations.

---

**Example before/after for a function:**

Before:

```python
def add_point(x, y, z=None):
  ...
```
After:

```python
def add_point(x: float, y: float, z: Optional[float] = None) -> None:
  ...
```