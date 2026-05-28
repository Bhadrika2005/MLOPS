import cv2
import os


output_folder = "frames"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)


video_path = r"C:\Users\BHADRIYA\Downloads\Vandalism005_x264.mp4\Vandalism005_x264.mp4"


cap = cv2.VideoCapture(video_path)

# Check video opened or not
if not cap.isOpened():
    print("Error opening video file")
    exit()


framerate = int(cap.get(cv2.CAP_PROP_FPS))

framecount = 0
count = 0

while True:

    success, frame = cap.read()

    if not success:
        break

    frame = cv2.resize(frame, (1280, 720))

    framecount += 1

   
    if framecount % (framerate // 4) == 0:

        filename = os.path.join(
            output_folder,
            f"frame_{count}.jpg"
        )

        cv2.imwrite(filename, frame)

        print("Saved:", filename)

        count += 1

cap.release()
cv2.destroyAllWindows()

print("Finished extracting frames")