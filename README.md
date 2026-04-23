# CS426_Project
Steganography Tool Research - Authors: Addison Junkins and Rosa Farinaccio
_______

This is the README for our Final Project for our course, CS426 - Digital Forensics.

______
 For Pythons Stegano Library

 python_stegano.py - Our Python Algorithm that uses the Stegano Python library.
In order to run, ensure python_stegano.py, your message .txt file, and a folder with the images you want to embed are all within the same folder/directory

After that ensure you have python installed.
  Check by running in terminal: 
   python --version OR py --version

TO RUN python_stegano.py
  1. Ensure the correct libraries are installed.
     - Check by running in terminal:
     - pip install stegano pillow

3. Once all the dependencies are installed, simply type into terminal:
   - python python_stegano batch-hide
   - This is to hide a stack of images with the same hidden file message.

5. You can reveal a message for a particular image by simply doing:
   - python python_stegano.py reveal --image (your folder with embedded images)\image_name
   - Example: python python_stegano.py reveal --image ENCODED\IMG_0716_hidden.bmp
