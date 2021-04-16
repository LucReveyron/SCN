import os
import cv2

path = './photos/'

print('First enter your first and last name without capital letter : \n')
print('Firstname: \n')
first_name = input('Enter firstname: ')
print('\n')
print('Lastname: \n')
last_name = input('Enter lastname: ')

# Create folder name
folder_name = first_name + '_' + last_name
print(folder_name)
# Create directory
path = path + folder_name

try:
    os.mkdir(path)
except OSError:
    print ("Creation of the directory %s failed" % path)
else:
    print ("Successfully created the directory %s " % path)

# Take pictures 

print('Now we take pictures of you.\n Press SPACE to take a picture.\n Try to change your face expression, hair position ect..\n')
print('When you have finish press ESC !\n')

list_pictures = []

#cam = cv2.VideoCapture(0)
adress = '192.168.1.24'
user = 'Smartcap1'
password = 'ProjectSCN2021'
cam = cv2.VideoCapture('rtsp://{user}:{passw}@{adress}/stream2')

cv2.namedWindow("test")

img_counter = 0

while True:
    ret, frame = cam.read()
    if not ret:
        print("failed to grab frame")
        break
    cv2.imshow("test", frame)

    k = cv2.waitKey(1)
    if k%256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    elif k%256 == 32:
        # SPACE pressed
        list_pictures.append(frame)
        img_name = "{}.jpg".format(img_counter)
        cv2.imwrite(os.path.join(path , img_name), frame)
        print("{} written!".format(img_name))
        img_counter += 1

cam.release()

cv2.destroyAllWindows()

# Do data augmentation
for img in list_pictures:
    # rotation
    list_rotation = [5,10,20,30,40] 

    rows,cols, ch = img.shape

    for rot in list_rotation:

        M = cv2.getRotationMatrix2D((cols/2,rows/2),rot,1)
        dst = cv2.warpAffine(img,M,(cols,rows))
        img_name = "{}.jpg".format(img_counter)
        cv2.imwrite(os.path.join(path , img_name), dst)
        img_counter += 1


