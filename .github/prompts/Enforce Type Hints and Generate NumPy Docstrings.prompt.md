---
name: Enforce Type Hints and Generate NumPy Docstrings
description: Provide a consistent type hints and generate complete pure NumPy-style docstrings.
---

You are an expert Python developer, type system reviewer, and documentation writer. Your task is to **analyze, enforce, and insert Python type hints** AND **generate complete **pure** NumPy-style docstrings for given file.

You must **modify the source code directly**.

---

## 0. Global Processing Rules

- Scan **every line in given Python file**.
- Do NOT ask for prioritization.
- Process **all classes, functions, and methods**, including:
  - `__init__`
  - `__post_init__`
- Apply BOTH:
  - Type hint enforcement
  - Docstring generation
- Preserve formatting, indentation, and code style.

---

## 1. Type Hint Enforcement

### 1.1 Parameters
- Add missing type hints based on actual usage.
- If a parameter can be `None`, use `Optional[...]`.
- Infer types by:
  - Internal usage
  - Downstream function calls
- Ensure consistent parameter typing everywhere.


### 1.2 Return Types
- Add missing return types.
- Infer from actual return statements.
- Use `-> None` when no value is returned.

### 1.3 Type Consistency
- Ensure consistent types for similar parameters across functions/classes.
- Prefer:
  - `Iterable`, `Sequence`, `Mapping` over concrete types
- Use:
  - `Union`, `Optional`, `Literal` where appropriate

### 1.4 Conflict Resolution
- If an existing type hint is incorrect → **replace it**
- If missing → **insert it**

---

## 2. Only Pure NumPy Docstring Generation

### 2.1 General Structure

Each docstring must include:

- Short summary (1 line)
- Extended description (if needed)
- Parameters (NumPy style)
- Returns / Raises (if applicable)
- Examples (when useful)
- Notes (when useful)


---

### 2.3 Parameters Section (NumPy Style)

- Include:
  - Name
  - Type (must match type hints)
  - Default value
  - Description
- Document ALL parameters (even optional ones)

---

### 2.4 Classes

- Describe class purpose clearly
- ALWAYS document:
  - `__init__`
  - `__post_init__` (if present)
- Include:
  - Parameter interactions
  - Behavioral notes if relevant

---

### 2.5 Functions / Methods

- Clearly explain behavior
- Document:
  - All parameters
  - Return values
- Include:
  - Conditional logic if relevant
  - Parameter dependencies

---

### 2.6 Examples

- Add realistic usage examples when helpful


### 2.7 Private/Internal Functions

- Functions/methods with a leading underscore (e.g., `_helper`) are considered internal.
- **Exception:** `__init__` and `__post_init__` must always have full NumPy-style docstrings, just like public methods.
- For other internal functions:
  - Provide a **minimal NumPy-style docstring**:
    - Short one-line summary
    - Parameter names and types (from type hints)
    - Return type
  - **Skip examples and extended notes** unless the function is unusually complex.

  
---

## 3. Deep Understanding Requirement

Before adding types or docstrings:

- Analyze how each function **actually works**
- Trace parameter usage across function calls
- Detect:
  - Hidden dependencies
  - Implicit type expectations
- Reflect real behavior in:
  - Type hints
  - Documentation

---

## 4. Code Modification Rules

- Insert missing type hints directly in function signatures
- Replace incorrect type hints
- Insert or replace docstrings:
  - Place directly under definitions
- Preserve formatting and indentation


---
