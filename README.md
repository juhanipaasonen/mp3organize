This is a simple script to sanitize and move mp3 files based on ID3 information.
Script reads all files and (sub-)folders under working directory.

Tracks are sorted to three kinds of contexts:
1. "ordinary" albums
    Album is considered ordinary, if all tracks with same album name have the same artist
2. compilation albums
    Album is considered a compilation, if it's not ordinary
3. tracks outside albums
    Track is outside albums, if there is no track number or there's no album tag.

Licensed under Creative Commons Attribution-ShareAlike 
(http://creativecommons.org/licenses/by-sa/3.0/)[CC BY-SA]
