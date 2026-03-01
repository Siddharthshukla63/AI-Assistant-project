import cv2
import os
import numpy as np
import csv
import sys
from datetime import datetime

# Load face cascade - get the correct path
cascade_path = os.path.join(os.path.dirname(__file__), 'lbpcascade_frontalface.xml')
if not os.path.exists(cascade_path):
    cascade_path = 'lbpcascade_frontalface.xml'  # Fallback to current directory

face_cascade = cv2.CascadeClassifier(cascade_path)
if face_cascade.empty():
    print(f"ERROR: Could not load cascade classifier from {cascade_path}")
    print("Make sure 'lbpcascade_frontalface.xml' is in the script directory!")

# Subjects: ID -> Name (add more students)
subjects = ["", "Your Name", "Student 2", "Student 3"]  # s1, s2, s3 folders

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
    faces, labels = [], []
    for dir_name in os.listdir(data_folder_path):
        if not dir_name.startswith("s"):
            continue
        label = int(dir_name.replace("s", ""))
        subject_path = os.path.join(data_folder_path, dir_name)
        for img_name in os.listdir(subject_path):
            if img_name.startswith("."):
                continue
            img_path = os.path.join(subject_path, img_name)
            image = cv2.imread(img_path)
            if image is None:
                continue
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

def log_attendance(name, student_id):
    """Log attendance to CSV with timestamp"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = os.path.exists('attendance.csv') and os.path.getsize('attendance.csv') > 0
    try:
        with open('attendance.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Name', 'ID', 'Time', 'Date'])
            writer.writerow([name, student_id, now.split()[1], now.split()[0]])
    except Exception as e:
        print(f"Error writing to attendance.csv: {e}")

def predict(test_img, face_recognizer, attended_today=None):
    if attended_today is None:
        attended_today = {}
    if test_img is None:
        return None
    img = test_img.copy()
    face, rect = detect_face(img)
    if face is None:
        return img
    
    label, confidence = face_recognizer.predict(face)
    
    if confidence < 100 and 0 <= label < len(subjects):  # Authenticated
        name = subjects[label]
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Mark attendance only once per day
        if name not in attended_today.get(today, []):
            log_attendance(name, label)
            attended_today.setdefault(today, []).append(name)
            status = f"{name} - Attendance Marked!"
        else:
            status = f"{name} - Already Present"
    else:
        status = "Unknown Person"
    
    draw_rectangle(img, rect)
    draw_text(img, status, rect[0], rect[1] - 5)
    return img

# === CAPTURE MODE (Run once per student) ===
def capture_images(student_id=1, count=20):
    # Check if cascade is loaded
    if face_cascade.empty():
        print("ERROR: Cascade classifier not loaded. Cannot detect faces!")
        return
        
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Cannot open camera!")
        print("Troubleshooting:")
        print("1. Check if camera is connected")
        print("2. Check if another application is using the camera")
        print("3. Try using camera index 1: cv2.VideoCapture(1)")
        return
    output_dir = os.path.join("training-data", f"s{student_id}")
    os.makedirs(output_dir, exist_ok=True)
    saved = 0
    
    print(f"Capturing {count} images for s{student_id}...")
    while saved < count:
        ret, frame = cap.read()
        if not ret:
            continue
            
        gray, rect = detect_face(frame)
        if gray is not None and rect is not None:
            cv2.rectangle(frame, (rect[0], rect[1]), 
                         (rect[0]+rect[2], rect[1]+rect[3]), (0,255,0), 2)
            cv2.putText(frame, f"Press SPACE to save ({saved}/{count})", 
                       (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)
            
            cv2.imshow(f"Capture s{student_id}", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord(' '):
                img_path = os.path.join(output_dir, f"{saved}.jpg")
                cv2.imwrite(img_path, frame)
                saved += 1
                print(f"Saved image {saved}")
            elif key == ord('q'):
                break
    cap.release()
    cv2.destroyAllWindows()

# MAIN EXECUTION
if __name__ == "__main__":
    # First check if cascade is loaded
    if face_cascade.empty():
        print("ERROR: Face cascade classifier failed to load!")
        print("Please ensure 'lbpcascade_frontalface.xml' exists in the same directory as this script")
        sys.exit(1)
    
    mode = input("Enter mode (1=capture, 2=attendance): ")
    
    if mode == "1":
        student_id = int(input("Student ID (1,2,3...): "))
        capture_images(student_id)
    else:
        # Training
        print("Training model...")
        faces, labels = prepare_training_data("training-data")
        if len(faces) == 0:
            print("Error: No training data found! Please capture images first.")
            sys.exit(1)
        try:
            face_recognizer = cv2.face.LBPHFaceRecognizer_create()
            face_recognizer.train(faces, np.array(labels))
            face_recognizer.save('trainer.yml')
            print("Model trained and saved!")
            
            # Attendance mode
            attended_today = {}
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("Error: Cannot open camera for attendance!")
                print("Troubleshooting:")
                print("1. Ensure camera is connected and not in use")
                print("2. Try camera index 1: cv2.VideoCapture(1)")
                sys.exit(1)
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                frame = predict(frame, face_recognizer, attended_today)
                if frame is not None:
                    cv2.imshow("Attendance System", frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            cap.release()
            cv2.destroyAllWindows()
            print("Check attendance.csv for records!")
        except Exception as e:
            print(f"Error during training or attendance: {e}")
            sys.exit(1)
