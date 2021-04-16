import cv2

# Load the cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def face_detection(person_frame):
    face_list = []
    gray = cv2.cvtColor(person_frame, cv2.COLOR_BGR2GRAY)
    # Detect the faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    # Draw the rectangle around each face
    for (x, y, w, h) in faces:
        #cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
        # Extract part of the frame 
        face_list.append(person_frame[y:y+h,x:x+w]) 
    if len(face_list) == 0: 
        return None
    else:
        return face_list[0]

