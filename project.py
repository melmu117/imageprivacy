#!/usr/bin/env python3

import sys
import math
import base64
import tkinter
import numpy

from io import BytesIO
from PIL import Image as PILImage

class Image_Privacy:
	def __init__(self, width, height, pixels):
	    self.width = width
	    self.height = height
	    self.pixels = pixels

	def generate_matrix(self, color):
	    """
	    Generates a transformation matrix for the specified color.
	    Inputs:
	        color: string with exactly one of the following values:
	               'red', 'blue', 'green', or 'none'
	    Returns:
	        matrix: a transformation matrix corresponding to
	                deficiency in that color
	    """
	    if color == 'red':
	        c = [[.567, .433, 0],[.558, .442, 0],[0, .242, .758]]
	    elif color == 'green':
	        c = [[0.625,0.375, 0],[ 0.7,0.3, 0],[0, 0.142,0.858]]
	    elif color == 'blue':
	        c = [[.95, 0.05, 0],[0, 0.433, 0.567],[0, 0.475, .525]]
	    elif color == 'none':
	        c = [[1, 0., 0],[0, 1, 0.],[0, 0., 1]]
	    return c


	def matrix_multiply(self, m1,m2):
	    """
	    Multiplies the input matrices.
	    Inputs:
	        m1,m2: the input matrices
	    Returns:
	        result: matrix product of m1 and m2
	        in a list of floats
	    """

	    product = numpy.matmul(m1,m2)
	    if type(product) == numpy.int64:
	        return float(product)
	    else:
	        result = list(product)
	        return result

	#gets each pixel and considers out of bounds cases
	def get_pixel(self, x, y):
	    width = self.width
	    height = self.height
	    #print(y*self.width + x)
	    if 0 <= x < width and 0 <= y < height:
	        return self.pixels[y*width+x]
	    elif x < 0 and 0 <= y < height:
	        return self.pixels[y*width]
	    elif y < 0 and 0 <= x < width:
	        return self.pixels[x]
	    elif x >= width and 0 <= y < height:
	        return self.pixels[y*width+width-1]
	    elif y >= height and 0 <= x < width:
	        return self.pixels[(height-1)*width+x]
	    elif x < 0 and y < 0:
	        return self.pixels[0]
	    elif x < 0 and y >= height:
	        return self.pixels[(height-1)*width]
	    elif x >= width and y < 0:
	        return self.pixels[width-1]
	    elif x >= width and y >= height:
	        return self.pixels[-1]

	def apply_filter(self, color):
	    """
	    pixels: a list of pixels in RGB form, such as [(0,0,0),(255,255,255),(38,29,58)...]
	    color: 'red', 'blue', 'green', or 'none', must be a string representing the color
	    deficiency that is being simulated.
	    returns: list of pixels in same format as earlier functions,
	    transformed by matrix multiplication
	    """
	    #creates a new list of the pixel values with color blindness
	    deficient_pixels = []
	    #gets the matrix value to multiply by for a certain color deficiency
	    matrix = generate_matrix(color)
	    #converts the list of tuples to list of arrays in order to be matrix multiplied
	    pixel_vectors = numpy.asarray(self.pixels)
	    #for each array of (R,G,B) values
	    for p in pixel_vectors:
	        #mulitply the deficiency matrix by the pixel value and converts to integer and tuples
	        deficiency_effect = matrix_multiply(matrix,p)
	        deficiency_effect = [int(x) for x in deficiency_effect]
	        deficient_pixels.append(tuple(deficiency_effect))
	    return deficient_pixels

	def get_BW_lsb(self):
	    """
	    Gets the least significant bit of each pixel in the specified image.
	    Inputs:
	       pixels: list, a list of pixels in BW form, such as [0, 255, 120, ...]
	    returns:
	       ls: a list of least significant bits
	    """
	    #initiates new list for least significant bits of each pixel
	    ls = []
	    #iterates through every pixel value in the list
	    for p in self.pixels:
	        #converts it to binary and adds the last digit (lsb) to the lsb list
	        binary = bin(p)
	        last_digit = binary[-1]
	        ls.append(int(last_digit))
	    return ls


	def get_RGB_lsb(self):
	    """
	    Gets the 2 least significant bits of each pixel in the specified color image.
	    Inputs:
	        pixels: a list of pixels in RGB form, such as [(0,0,0),(255,255,255),(38,29,58)...]
	    Returns:
	        ls: a list of least significant bits
	    """
	    #initiates new list for least significant bits of each pixel
	    ls = []
	    #iterates through every pixel tuple in the list
	    for colors in self.pixels:
	        #creates a new tuple for each corresponding tuple in the pixel value list
	        color_tuple = ()
	        #iterates through the tuples in pixel values
	        for p in colors:
	            #converts each value in the tuple to a binary and gets the last two digits
	            binary = bin(p)
	            last_digit = binary[-1]
	            second_ls = binary[-2]
	            #if there is no second lsb, then it just sets the the value to the one lsb
	            if binary[-2] == 'b':
	                #adds the lsb of each value in the tuple to a new tuple
	                color_tuple += (int(last_digit),)
	            else:
	                color_tuple += (int(last_digit)+2*int(second_ls),)
	        #appends the least significant bit tuple to the new lsb list
	        ls.append(color_tuple)
	    return ls

	#takes a point and changes the corresponding value in the pixel list
	def set_pixel(self, x, y, c):
	    self.pixels[y*self.width + x] = c

	#applies a function to each pixel in a picture
	def apply_per_pixel(self, func):
	    result = Image.new(self.width, self.height)
	    #iterates through each pixel
	    for x in range(result.width):
	        for y in range(result.height):
	            color = self.get_pixel(x, y)
	            newcolor = func(color)
	            result.set_pixel(x, y, newcolor)
	    return result

	#goes through each pixel, rounds decimals, changes negatives to 0, and over 255 to 255
	def clip_pixels(self):
	    #print(self.pixels)
	    pixels = self.pixels
	    for i in range(len(pixels)):
	        if pixels[i] > 255:
	            pixels[i] = 255
	        elif pixels[i] < 0:
	            pixels[i] = 0
	        else:
	            pixels[i] = round(pixels[i])
	    #print(pixels)
	    return Image(self.width, self.height, pixels)

	#takes a pixel at (x,y) and finds the values of the pixels in an n x n box around it
	def get_correlation_pixel_for_one(self, x, y, kernal_size):
	    pixel_list = []
	    for m in range(int(-(kernal_size-1)/2), int((kernal_size-1)/2+1)):
	        for n in range (int(-(kernal_size-1)/2), int((kernal_size-1)/2+1)):
	            pixel_list.append(self.get_pixel(x+n, y+m))
	    return pixel_list

	#takes a pixel at (x,y) and a kernal and multiplies each corresponding value to output a new pixel at (x,y)
	def new_pixel(self, x, y, kernal):
	    new_pixel=0
	    kernal_size = int(len(kernal)**0.5)
	    corresponding_pixels = self.get_correlation_pixel_for_one(x, y, kernal_size)
	    #print(kernal)
	    #print(corresponding_pixels)
	    for i in range(len(kernal)):
	        new_pixel += kernal[i]*corresponding_pixels[i]
	    return new_pixel

	#iterates through all x, y and outputs new_pixels for each coordinate based on kernal
	#returns new list of pixels
	def get_all_correlation_pixels(self, kernal):
	    new_pixels = []
	    for y in range(self.height):
	        for x in range(self.width):
	            new_pixels.append(self.new_pixel(x, y, kernal))
	    return new_pixels

	#outputs a new image with correlation kernal and clips the pixels
	def correlation(self, kernal):
	    new_image = Image(self.width, self.height, self.get_all_correlation_pixels(kernal)).clip_pixels()
	    return new_image

	#inverts a picture by subtracting each pixel value from 255
	def inverted(self):
	    return self.apply_per_pixel(lambda c: 255-c)

	#creates a n x n kernal for a blur (each value is sqrt of n)
	def blur_kernal(self,n):
	    kernal = []
	    for i in range(n**2):
	        kernal.append(n**(-2))
	    #print(kernal)
	    return kernal

	#creates a blur kernal from a given size, creates a new list of correlation pixels from the kernal
	#returns a new image altered with blur kernal
	def blurred(self, n):
	    width = self.width
	    height = self.height
	    kernal = self.blur_kernal(n)        
	    correlation_blur = self.get_all_correlation_pixels(kernal)
	    blurred_i = Image(self.width,self.height,correlation_blur).clip_pixels()
	    return blurred_i

	#creates a blur kernal and an identity kernal (0's everywhere except middle square with 1)
	#subtracts every value from blur kernal from two times identity kernal to get kernal for sharpening
	#returns a sharpened image of using sharpened kernal
	def sharpened(self, n):
	    blur_kernal = self.blur_kernal(n)
	    identity_kernal = []
	    for i in range (n**2):
	        if i == int(n**2/2):
	            identity_kernal.append(1)
	        else:
	            identity_kernal.append(0)
	    sharpen_kernal = []
	    for i in range(n**2):
	        sharpen_kernal.append(2*identity_kernal[i] - blur_kernal[i])
	    correlation_sharpen = self.get_all_correlation_pixels(sharpen_kernal)
	    sharpened_i = Image(self.width,self.height,correlation_sharpen).clip_pixels()
	    return sharpened_i

	#creates two lists of pixels after using x-kernal and y-kernal for edges
	#applies the edge equation for x and y images for every pixel in image
	#returns the final image after edge transformations
	def edges(self):
	    K_x = [-1,0,1,-2,0,2,-1,0,1]
	    K_y = [-1,-2,-1,0,0,0,1,2,1]
	    correlation_x = self.get_all_correlation_pixels(K_x)
	    correlation_y = self.get_all_correlation_pixels(K_y)
	    final_pixels = []
	    for i in range(len(correlation_x)):
	        final_pixels.append((correlation_x[i]**2 + correlation_y[i]**2)**0.5)
	    final_i = Image(self.width, self.height, final_pixels).clip_pixels()
	    return final_i

	def __eq__(self, other):
	    return all(getattr(self, i) == getattr(other, i)
	               for i in ('height', 'width', 'pixels'))

	def __repr__(self):
	    return "Image(%s, %s, %s)" % (self.width, self.height, self.pixels)

	@classmethod
	def load(cls, fname):
	    """
	    Loads an image from the given file and returns an instance of this
	    class representing that image.  This also performs conversion to
	    grayscale.

	    Invoked as, for example:
	       i = Image.load('test_images/cat.png')
	    """
	    with open(fname, 'rb') as img_handle:
	        img = PILImage.open(img_handle)
	        img_data = img.getdata()
	        if img.mode.startswith('RGB'):
	            pixels = [round(.299*p[0] + .587*p[1] + .114*p[2]) for p in img_data]
	        elif img.mode == 'LA':
	            pixels = [p[0] for p in img_data]
	        elif img.mode == 'L':
	            pixels = list(img_data)
	        else:
	            raise ValueError('Unsupported image mode: %r' % img.mode)
	        w, h = img.size
	        #print(fname + " " + str(w) + " " + str(h))
	        return cls(w, h, pixels)

	@classmethod
	def new(cls, width, height):
	    """
	    Creates a new blank image (all 0's) of the given height and width.

	    Invoked as, for example:
	        i = Image.new(640, 480)
	    """
	    return cls(width, height, [0 for i in range(width*height)])

	def save(self, fname, mode='PNG'):
	    """
	    Saves the given image to disk or to a file-like object.  If fname is
	    given as a string, the file type will be inferred from the given name.
	    If fname is given as a file-like object, the file type will be
	    determined by the 'mode' parameter.
	    """
	    out = PILImage.new(mode='L', size=(self.width, self.height))
	    out.putdata(self.pixels)
	    if isinstance(fname, str):
	        out.save(fname)
	    else:
	        out.save(fname, mode)
	    out.close()

	def gif_data(self):
	    """
	    Returns a base 64 encoded string containing the given image as a GIF
	    image.

	    Utility function to make show_image a little cleaner.
	    """
	    buff = BytesIO()
	    self.save(buff, mode='GIF')
	    return base64.b64encode(buff.getvalue())

	def show(self):
	    """
	    Shows the given image in a new Tk window.
	    """
	    global WINDOWS_OPENED
	    if tk_root is None:
	        # if tk hasn't been properly initialized, don't try to do anything.
	        return
	    WINDOWS_OPENED = True
	    toplevel = tkinter.Toplevel()
	    canvas = tkinter.Canvas(toplevel, height=self.height,
	                            width=self.width, highlightthickness=0)
	    canvas.pack()
	    canvas.img = tkinter.PhotoImage(data=self.gif_data())
	    canvas.create_image(0, 0, image=canvas.img, anchor=tkinter.NW)
	    def on_resize(event):
	        # handle resizing the image when the window is resized
	        # the procedure is:
	        #  * convert to a PIL image
	        #  * resize that image
	        #  * grab the base64-encoded GIF data from the resized image
	        #  * put that in a tkinter label
	        #  * show that image on the canvas
	        new_img = PILImage.new(mode='L', size=(self.width, self.height))
	        new_img.putdata(self.pixels)
	        new_img = new_img.resize((event.width, event.height), PILImage.NEAREST)
	        buff = BytesIO()
	        new_img.save(buff, 'GIF')
	        canvas.img = tkinter.PhotoImage(data=base64.b64encode(buff.getvalue()))
	        canvas.configure(height=event.height, width=event.width)
	        canvas.create_image(0, 0, image=canvas.img, anchor=tkinter.NW)
	    # finally, bind that function so that it is called when the window is
	    # resized.
	    canvas.bind('<Configure>', on_resize)
	    toplevel.bind('<Configure>', lambda e: canvas.configure(height=e.height, width=e.width))

	    # when the window is closed, the program should stop
	    toplevel.protocol('WM_DELETE_WINDOW', tk_root.destroy)

	def reveal_image(self, mode):
	    """
	    Extracts the hidden image, calls get lsb function based on parameter

	    Inputs: 
	        filename: string, input file to be processed
	        mode: 'RGB' or '1' based on whether input file is color ('RGB') or black/white ('1'); see PIL Modes
	    Returns:
	        result: an Image object containing the hidden image
	    """
	    #first converts the image to a list of pixels
	    #opens the image to obtain the size
	    width, height = self.width, self.height
	    #creates a new list to produce an image with more contrast
	    updated_pixels = []
	    #if the picture is in black and white
	    if mode == '1':
	        #obtains the lsb for the black and white photo
	        new_pixels = get_BW_lsb(self.pixels)
	        #iterates through the list of least significant bits
	        for value in new_pixels:
	            #multiplies each 0 or 1 by 255 to create 0 or 255 in order to see contrast
	            value = value*252
	            #creates a new list of these larger contrasts
	            updated_pixels.append(value)
	        #creates a new black and white image of the original size
	        bw_pic_out = Image.new("1",(width,height))
	        #adds the final bw updated pixel list to the image
	        bw_pic_out.putdata(updated_pixels)
	        #saves the image so that it can be opened and returned
	        bw_pic_out.save('pic_out.png')
	        pic = Image.open('pic_out.png')
	        return pic
	    #if the picture is in color
	    else:
	        #obtains the lsb for the color photo
	        new_pixels = get_RGB_lsb(self.pixels)
	        #iterates through the list of tuples of lsb
	        for rgb in new_pixels:
	            #creates a new tuple for each corresponding tuple in the pixel lsb list
	            updated_tuple = ()
	            #iterates through the values in the lsb tuples
	            for value in rgb:
	                #multiplies each value by 255 in order to create a larger contrast
	                value = int(value*255/3)
	                #adds the modified value from the tuple to the new tuple
	                updated_tuple += (value,)
	            #appends each updated tuple to the new list of modified lsb tuples
	            updated_pixels.append(updated_tuple)
	        #returns an image from the updated list of lsb values with the original size
	        return convert_pixels_to_image(updated_pixels,(width,height))

try:
    tk_root = tkinter.Tk()
    tk_root.withdraw()
    tcl = tkinter.Tcl()
    def reafter():
        tcl.after(500,reafter)
    tcl.after(500,reafter)
except:
    tk_root = None
WINDOWS_OPENED = False

if __name__ == '__main__':
    
    pass
    
    if WINDOWS_OPENED and not sys.flags.interactive:
        tk_root.mainloop()
