# image to ascii
A .jpg/.jpeg/.png image to ASCII art .svg converter written in Python, inspired by the Image to ASCII Coding Challenge by Coding Train on YouTube.

The script uses `pillow` to read images, increase contrast, then bring in the raw RGB data. 
The RGB data is used to calculate luminance for each pixel, and then mapped to a character in a density string
`"Ñ@#W$9876543210?!abc;:+=-,.   "` which is a string of ASCII characters listed in order of decreasing brightness.
