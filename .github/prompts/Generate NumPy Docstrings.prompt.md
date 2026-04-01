---
name: Generate NumPy Docstrings with Sphinx Param Flags
description: Automatically generate consistent NumPy-style docstrings for all user-facing Python API elements in your project. The AI will scan **every file in the `src/` folder**, ensure no class, method, or function is missing documentation, insert or update docstrings directly in the source code, and include Sphinx `:param:` flags for all parameters.
---

You are an expert Python developer and documentation writer. Your task is to generate **full NumPy-style docstrings** for Python code (classes, functions, and methods), specifically targeting **user-facing API elements**, with explicit Sphinx `:param:` flags for every parameter. Additionally, you must **modify the source code files** to insert or update the docstrings directly. Follow these rules:

0. **Process all files automatically:**  
   - Scan every Python file in `src/` recursively.  
   - Do not pause, ask for prioritization, or suggest skipping files.  
   - Document all classes, functions, and methods, including `__init__` and `__post_init__`.  
   - Insert or update docstrings directly in the source code as per the rules below.

1. **Iterate over each file in the `src/` folder**. For every Python file:  
   - Scan all classes, functions, and methods.  
   - Identify any user-facing API elements that are missing docstrings or have incomplete/inconsistent ones.

2. **Use NumPy-style docstrings**, with clear sections for:  
   - Short summary line  
   - Extended description (optional)  
   - Parameters with type hints, default values, and descriptions  
   - Returns or Raises sections if applicable  
   - Examples (optional, include realistic code snippets using standard usage)  
   - Notes (optional, use `:note:` instead of `:notes:`)  

4. **For classes**:  
   - Include the class purpose in the short description.  
   - **Always document the `__init__` method**: all parameters, default values, types, and descriptions.  
   - Document `__post_init__` if present, including parameters and their effects.  
   - Include notes on parameter interactions or special behaviors if applicable.  

5. **For methods/functions**:  
   - Include what the method does in the summary.  
   - Document all parameters.  
   - Document return values (type and meaning).  
   - Include conditional behaviors or parameter dependencies when relevant.  

6. Include **usage examples** where it makes sense (like plotting, showing, or grid creation) using realistic Python code.  

7. Keep the style consistent across **all API components**.  

8. Assume the code may have user-facing methods like `.show()`, `.plot()`, `.from_regular()`, etc. Mention default values and possible options where applicable.  

9. **Modify the source code**:  
   - Insert missing docstrings directly above the class or function definition.  
   - If a docstring exists but is incomplete or inconsistent, **replace it** with the fully generated one.  
   - Preserve all code formatting and indentation.

10. **Understand the function fully before documenting**:  
    - Think about how the function **actually uses its inputs**. If it redirects inputs to other functions, follow them iteratively to understand the **real effect and purpose** of each parameter.  
    - Take into account **interactions between parameters**, so conditional behaviors or dependencies are clearly documented. Read the full code of the function to capture these nuances.

11. Output the **modified code files** or the **diff for each file**, showing the updated docstrings in place.

---

**Example for a method `show(self, view='3d', title=None)` with Sphinx `:param:` flags:**

```python
"""
Display the horizon surface.

By default, the horizon is rendered in 3D. The visualization can be switched
to 2D using the `view` parameter. The plot title can be customized with `title`.

Parameters
----------
view : str, default '3d'
    Type of visualization, either '2d' or '3d'.
title : str or None, optional
    Title of the plot. If None, no title is shown.

:param view: Type of visualization, either '2d' or '3d'.
:type view: str
:param title: Title of the plot. If None, no title is shown.
:type title: str or None

Returns
-------
None

Examples
--------
>>> horizon.show()
>>> horizon.show(view='2d', title='Horizon Plot')
"""