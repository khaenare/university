from image_io import read_grayscale_image

X = read_grayscale_image("x3.bmp")
Y = read_grayscale_image("y8.bmp")

print(X.shape, Y.shape, X.min(), X.max(), Y.min(), Y.max())
