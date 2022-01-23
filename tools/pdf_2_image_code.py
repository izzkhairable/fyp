from pdf2image import convert_from_path, convert_from_bytes
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import csv

try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'
images = convert_from_path('input.pdf', poppler_path='C:\\Program Files\\poppler-21.11.0\\Library\\bin', output_folder='output', output_file='test', fmt='jpg')
