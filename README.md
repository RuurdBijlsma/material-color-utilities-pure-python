# material-color-utilities-python

[![Chat on Matrix](https://matrix.to/img/matrix-badge.svg)](https://matrix.to/#/#AdwCustomizer:matrix.org)

Python port of material-color-utilities used for Material You colors

Original source code: https://github.com/material-foundation/material-color-utilities

NOTE: This is an **unofficial** port of material-color-utilities from JavaScript to Python

## Build and install

You need to have [Poetry](https://python-poetry.org) installed

```shell
poetry build
poetry install
```

## Usage examples for Themeing

Theme from color:

``` python
from material_color_utilities_python import *

theme = theme_from_source_color(argb_from_hex('#4285f4'))

print(theme)
```

Color from image:

``` python
from material_color_utilities_python import *

img = Image.open('path/to/image.png')
argb = source_color_from_image(img)

print(hex_from_argb(argb))
```

Theme from image:

``` python
from material_color_utilities_python import *

img = Image.open('/path/to/image')
basewidth = 64
wpercent = (basewidth/float(img.size[0]))
hsize = int((float(img.size[1])*float(wpercent)))
img = img.resize((basewidth,hsize),Image.Resampling.LANCZOS)
print(theme_from_image(img))

print(theme)
```
