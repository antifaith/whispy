#! /usr/bin/env python
######################################################################
# tuner.py - a minimal command-line guitar/ukulele tuner in Python.
# Requires numpy and pyaudio.
######################################################################
# Author:  Matt Zucker
# Date:    July 2016
# License: Creative Commons Attribution-ShareAlike 3.0
#          https://creativecommons.org/licenses/by-sa/3.0/us/
######################################################################
#  /l、     
# (°､ 。７     
#  l  ~～ヽ 
#  じ し f_,)√  
# EDITED BY SPOONY BARD TO BE A WHISTLE DETECTOR!!!!!
#SB: All code not by original author preceded by "SB:"

import numpy as np
import pyaudio
#SB: Need to time whether notes are consecutive
import time as t

######################################################################
# Feel free to play with these numbers. Might want to change NOTE_MIN
# and NOTE_MAX especially for guitar/bass. Probably want to keep
# FRAME_SIZE and FRAMES_PER_FFT to be powers of two.

NOTE_MIN = 30       # A2
NOTE_MAX = 100       # A7
FSAMP = 32050       # Sampling frequency in Hz
FRAME_SIZE = 2048   # How many samples per frame?
FRAMES_PER_FFT = 8 # FFT takes average across how many frames?

######################################################################
# Derived quantities from constants above. Note that as
# SAMPLES_PER_FFT goes up, the frequency step size decreases (so
# resolution increases); however, it will incur more delay to process
# new sounds.

SAMPLES_PER_FFT = FRAME_SIZE*FRAMES_PER_FFT
FREQ_STEP = float(FSAMP)/SAMPLES_PER_FFT

######################################################################
# For printing out notes

NOTE_NAMES = 'C C# D D# E F F# G G# A A# B'.split()

######################################################################
# These three functions are based upon this very useful webpage:
# https://newt.phys.unsw.edu.au/jw/notes.html
def freq_to_number(f): return 69 + 12*np.log2(f/440.0)
def number_to_freq(n): return 440 * 2.0**((n-69)/12.0)
def note_name(n): return NOTE_NAMES[n % 12] + str(n/12 - 1)


#######################################################################
#SB: I declared some stuff here, a and a2 store input and input converted to intervals, SinceLastDetection and time are used for the timer
a = []
a2 = []
SinceLastDetection = 0
time = 0
#SB: This first function returns a relative note value so you don't have to whistle in A=440Hz, if you have perfect pitch or are using a tuned instrument and want to detect specific notes you can replace f2 with 440.0, this would make the test command A B C#
def relative_freq(f,f2): return 1200*np.log2(f/f2)
#SB: remove adjacent elements that match from a list, I got this here https://stackoverflow.com/questions/3460161/remove-adjacent-duplicate-elements-from-a-list
def remove_adjacent(nums):
  i = 1
  while i < len(nums):   
    if nums[i] == nums[i-1]:
      nums.pop(i)   
      i -= 1  
    i += 1
  return nums
#SB: I don't use this one and I'm not sure how well it works but it removes groups of 2 or less identical notes to reduce noise and transitional note detection, I decided to just scrub results for each command instead
#def remove_lonely(nums):
#    r = 1
#    while r < (len(nums)):
#        if nums[0] != nums[1]:
#           nums.pop(0)
#        r += 1    
#    i = 1
#    while i < (len(nums)-2):     
#        if i > 1:
#            if (nums[i] != nums[i-1] or nums[i+1]) and (nums[i-1] != nums[i-2] or nums[i]) and (nums[i+1] != nums[i+2] or nums[i]):
#                nums.pop(i)  
#        i += 1
#    return nums
#SB: this functions scrubs the results for each command, ie compares nums (unscrubbed note list) to listpopper (command list) and removes all entries in nums that do not exist in list popper. This is because whistling and environmental noise tends to produce lots of extra notes. I was having trouble with this and ConfusedReptile#6830 helped me finish this function on discord
def pop_list(nums,listpopper):
  i = 0
  while i < len(nums):
    el = nums[i]
    if el not in listpopper:
      nums.pop(i)
      i-=1
    i+=1
#SB: This function checks if A (command list) is contained in B (scrubbed note list), I got it from here https://www.geeksforgeeks.org/python-check-if-a-list-is-contained-in-another-list/
def contains(A, B): 
    for i in range(len(B)-len(A)+1): 
        for j in range(len(A)): 
            if B[i + j] != A[j]: 
                break
        else: 
            return True
    return False
    
    
######################################################################
# Ok, ready to go now.
# Get min/max index within FFT of notes we care about.
# See docs for numpy.rfftfreq()
def note_to_fftbin(n): return number_to_freq(n)/FREQ_STEP
imin = max(0, int(np.floor(note_to_fftbin(NOTE_MIN-1))))
imax = min(SAMPLES_PER_FFT, int(np.ceil(note_to_fftbin(NOTE_MAX+1))))

# Allocate space to run an FFT. 
buf = np.zeros(SAMPLES_PER_FFT, dtype=np.float32)
num_frames = 0

# Initialize audio
stream = pyaudio.PyAudio().open(format=pyaudio.paInt16,
                                channels=1,
                                rate=FSAMP,
                                input=True,
                                frames_per_buffer=FRAME_SIZE)

stream.start_stream()

# Create Hanning window function
window = 0.54 * (1 - np.cos(np.linspace(0, 2*np.pi, SAMPLES_PER_FFT, False)))

# Print initial text
print ('sampling at', FSAMP, 'Hz with max resolution of', FREQ_STEP, 'Hz')
print

# As long as we are getting data:

while stream.is_active():

    # Shift the buffer down and new data in
    buf[:-FRAME_SIZE] = buf[FRAME_SIZE:]
    buf[-FRAME_SIZE:] = np.fromstring(stream.read(FRAME_SIZE), np.int16)

    # Run the FFT on the windowed buffer
    fft = np.fft.rfft(buf * window)

    # Get frequency of maximum response in range
    freq = (np.abs(fft[imin:imax]).argmax() + imin) * FREQ_STEP

    # Get note number and nearest note
    n = freq_to_number(freq)
    n0 = int(round(n))

    # Console output once we have a full buffer
    num_frames += 1
    
    #SB: Get highest amplitude note... it's very similar to original author's freq
    amp = (np.abs(fft).argmax())
        
    #SB: The test command list: root > major 2nd > perfect 4th
    testcom = [0, 2, 4]

    #SB: detect notes with amp between 1500 and 400, around F7 and G5, edit if your whistling range is different but expect more noise and variance at lower and higher ranges
    if num_frames >= FRAMES_PER_FFT and 1500 > amp > 400 and 'SinceLastDetection' in vars():
        #SB: check timer to see how long it was since sampling a note in the proper range
        time = (t.perf_counter() - SinceLastDetection)
        #SB: add sampled frequency to list a if it was less than .25 sec since last append
        if time < .25:
            a.append(freq)
        #SB: debugging feedback, decomment if you want to see what's happening, also contains the original tuner feedback and notes in A=440Hz:
            #if len(a) >1:
                #print ('freq: {:7.2f} Hz     note: {:>3s} {:+.2f} amp: {:f} {:f} {}'.format(
                    #freq, note_name(n0), n-n0, amp, freq, len(a)))
        #SB: update timer
        SinceLastDetection = t.perf_counter()
        
        
    #SB: activate once it's been over .25 seconds since last detection, also requires a note or ambient detection to execute command detection >.25 seconds after a command
    if time > .25:
    #SB: interpret data gathered, first determine if probably whistled notes by length
        if len(a) >= 10:
            #SB: set relative root to the 3rd input to reduce the chance of noise and increase chance of getting intended note
            b = a[3]
            #SB: change frequencies to half step (100 cent) intervals relative to a[3] and store in list a2
            for x in a: 
                d = int(round(relative_freq(x,b)/100))
                a2.append(d)              
            #SB: remove adjacent notes so we just have a list of distinct notes
            remove_adjacent(a2)
            #SB: create a new list, a3, to scrub and compare to the command list
            a3 = a2.copy()
            #SB: remove all notes from a3 not contained in command list
            pop_list(a3,testcom)
            #SB: print the whole list of notes detected
            for x in range(len(a2)): 
                print (a2[x]), 
            #SB: print whether detection was successful
            print('{}'.format(contains(testcom,a3)))
        #SB: reset lists for next detection
        del a[:]
        del a2[:]
