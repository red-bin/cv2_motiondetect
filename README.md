# cv2_motiondetect
Redesign of some code found on some blog a long while back with lots of changes.
Let me know if the original code is yours so I can give you credit.

This is a security system designed for a first generation raspberry pi. 

Works by converting an image to greyscale, then running some bitwise magic across frames.  
Any differences cause a flare in brightness, which can be used for tracking motion.

For increased accuracy, this version does a movement check over an arbitrary amount of frames. 

Unfortunately, with increased accuracy comes a completely hosed gen1 pi. :)
