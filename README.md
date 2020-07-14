Based on: https://mzucker.github.io/2016/08/07/ukulele-tuner.html 

Original Author:  Matt Zucker

License: Creative Commons Attribution-ShareAlike 3.0
         https://creativecommons.org/licenses/by-sa/3.0/us/

Requires pyaudio, numpy, python (I used 3.8 because it's the only version I could get pyaudio to install on)

This is now a whistle detector... I recommend setting commands to be a given number of intervals in a row,  reaching your first note quickly and holding your first note to ensure it registers, and then sliding up and down to ensure you hit all the notes involved, it doesn't matter how many notes you hit between the notes of the command as long as they end up in the right order. A pause of .25 seconds and then the detection of another note pair activates the last string of notes with less than .25 seconds between them. This is still a very early alpha and this is the most Python I've ever wrote so it's messy and has no interface.

whispy.bat is just "python -m whispy.py"

The only command currently recognized is 0, 2, 4 or root, major second, perfect fourth. The program will output true if the whistled notes contain all 3 notes in that order and false otherwise. I whistle the first bar of whiskey before breakfast and it generally works, but it's far more consistent to slide up the scale to the 4th because the relative pitch detection might end up returning the wrong intervals.





Original Readme:

# python-tuner
Minimal command-line guitar/ukulele tuner in Python. 
Writeup at <https://mzucker.github.io/2016/08/07/ukulele-tuner.html>

To run:

    python tuner.py

...then pluck the strings!
