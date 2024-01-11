import cv2 as cv
import numpy as np

# Check if OpenCV was built with OpenCL support
if not cv.ocl.haveOpenCL():
    print("OpenCV was not built with OpenCL support")
    exit()

# Enable the use of OpenCL in OpenCV
cv.ocl.setUseOpenCL(True)

# Create UMat objects
src = np.eye(3, dtype=np.float32)
print(src)
srcUMat = cv.UMat(src)

# Perform a Gaussian blur on the GPU
dstUMat = cv.GaussianBlur(srcUMat, (3, 3), 0, borderType=cv.BORDER_DEFAULT)

# Download the result back to a regular numpy array
dst = dstUMat.get()

print(dst)