from PIL import Image 
 
  
img = Image.open(r"input.jpg") 
 
 
left = 161
top = 1306
right = 1589
bottom = 1996
 ##158, 1313, 1592, 1999
  
img_res = img.crop((left, top, right, bottom)).save("cropped.jpg")
 

# img_res.show() 
