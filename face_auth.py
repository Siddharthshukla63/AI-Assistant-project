import cv2
import os
import numpy as np

# Load face cascade
face_cascade = cv2.CascadeClassifier('lbpcascade_frontalface.xml')

# Subjects dictionary (add your name with ID 1)
subjects = ["", "Your Name"]  # ID 1 = Your Name

def detect_face(img):
    if img is None:
        return None, None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.2, 5)
    if len(faces) == 0:
        return None, None
    (x, y, w, h) = faces[0]
    return gray[y:y+h, x:x+w], faces[0]

def prepare_training_data(data_folder_path):
    if not os.path.exists(data_folder_path):
        print(f"Error: {data_folder_path} does not exist!")
        return [], []
    dirs = os.listdir(data_folder_path)
    faces = []
    labels = []
    for dir_name in dirs:
        if not dir_name.startswith("s"):
            continue
        label = int(dir_name.replace("s", ""))
        subject_dir_path = os.path.join(data_folder_path, dir_name)
        subject_images_names = os.listdir(subject_dir_path)
        for image_name in subject_images_names:
            if image_name.startswith("."):
                continue
            image_path = os.path.join(subject_dir_path, image_name)
            image = cv2.imread(image_path)
            face, rect = detect_face(image)
            if face is not None:
                faces.append(face)
                labels.append(label)
    return faces, labels

def draw_rectangle(img, rect):
    (x, y, w, h) = rect
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

def draw_text(img, text, x, y):
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)

def predict(test_img, face_recognizer):
    img = test_img.copy()
    face, rect = detect_face(img)
    if face is None:
        return img
    label, confidence = face_recognizer.predict(face)
    if confidence < 100 and 0 <= label < len(subjects):  # Threshold for authentication
        label_text = subjects[label] + " - Authenticated"
    else:
        label_text = "Unknown"
    draw_rectangle(img, rect)
    draw_text(img, label_text, rect[0], rect[1] - 5)
    return img

# === CAPTURE MODE (run once, comment out after) ===
def capture_images():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Cannot open camera!")
        return
    count = 0
    os.makedirs("training-data/s1", exist_ok=True)
    while count < 20:
        ret, frame = cap.read()
        if not ret:
            continue
        gray, rect = detect_face(frame)
        if gray is not None and rect is not None:
            cv2.rectangle(frame, (rect[0], rect[1]), (rect[0]+rect[2], rect[1]+rect[3]), (0,255,0), 2)
            cv2.putText(frame, f"Captured: {count+1}/20 (Press SPACE to save)", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)
            cv2.imshow("Capturing Faces - SPACE to save, Q to quit", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord(' '):  # SPACE saves
                cv2.imwrite(f"training-data/s1/{count}.jpg", frame)
                count += 1
            elif key == ord('q'):
                break
    cap.release()
    cv2.destroyAllWindows()
    print("Capture complete!")

capture_images()  # Run this FIRST - comment out after capturing images
# === END CAPTURE ===

# Step 1: Prepare training data (run once, needs 10-20 images in training-data/s1/)
print("Preparing data...")
faces, labels = prepare_training_data("training-data")
print("Total faces: ", len(faces))

if len(faces) == 0:
    print("Error: No training data found! Please capture images first.")
else:
    # Step 2: Train recognizer
    try:
        face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        face_recognizer.train(faces, np.array(labels))
        face_recognizer.save('trainer.yml')  # Save model
        print("Model trained and saved!")
        
        # Step 3: Real-time authentication
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Cannot open camera for authentication!")
        else:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                predicted_img = predict(frame, face_recognizer)
                cv2.imshow("Face Authentication", predicted_img)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            cap.release()
            cv2.destroyAllWindows()
    except Exception as e:
        print(f"Error during training or authentication: {e}")
