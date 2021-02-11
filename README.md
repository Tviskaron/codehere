# Codehere
Codehere is a tool to prepare your jupyter notebooks for seminars and homework.

# installing 

```
pip install git+https://github.com/Tviskaron/codehere.git
```

# usage in jupyter notebook

```
"""<comment>"""
from codehere import convert
import os

os.makedirs('render', exist_ok=True)

convert(clear=True, replacement=" Здесь ваш код ", outfile='render/task.ipynb')
convert(clear=True, solution=True, replacement=" Здесь ваш код ", outfile='render/solution.ipynb')
"""</comment>"""
```
