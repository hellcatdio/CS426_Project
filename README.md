# CS426_Project
Steganography Tool Research - Authors: Addison Junkins and Rosa Farinaccio
_______

This is the README for our Final Project for our course, CS426 - Digital Forensics.

There are two files you can utilize with various word lengths.
- message.txt (approx. 69 words)
- i_am_groot.txt (approx. 200,000+ words)
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

TO RUN steghide.py and openstego.py
You will need to install both steghide and openstego from their respective websites. For steghide, you will need to change the directory path in the python code to refelct the location of the steghide.exe file installed on your computer. For openstego, you will need to locate the openstego.jar file that will be on your computer after installation. Move that file into the main project folder so that the python code can recognize it.
Same with the stegano python library, ensure that you have the latest version of python installed.
Within both .py files, you will need to update the Directory path variables that correlate 
Use the following directory ("->" implies folder):
->Project
  ->input_dataset (clean images folder)
  ->logs (log folder)
  ->output (steghide output folder)
    ->extracted
    ->steghide
  ->reports (csv file output folder)
  ->extracted_openstegano 
  ->results_openstegano
  - steghide.py
  - openstego.py
  - openstego.jar
  - secret.txt (message file)

Running the code will automatically both embed and extract the message from the images using the respective tools. After running, the terminal will give a message notifying you to check the correct file folders for the results.
