import cv2
import time
import base64
import requests

API_URL = "http://localhost:8000/analyze"
CHECK_INTERVAL = 10 # Send an image every 10 seconds

def send_frame(frame):
    # Optimizing: Resize image to speed up transmission and processing
    frame_resized = cv2.resize(frame, (640, 480))
    _, buffer = cv2.imencode('.jpg', frame_resized)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    
    try:
        # We only send the image now. The prompt is handled by the backend!
        response = requests.post(API_URL, json={"image_base64": jpg_as_text})
        if response.status_code == 200:
            print(f"✅ AI: {response.json()['ai_response']}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Connect Error: {e}")

def main():
    cap = cv2.VideoCapture(0)
    last_time = time.time()
    print("📷 Camera Agent Running...")

    while True:
        ret, frame = cap.read()
        if not ret: break
        
        # Timer Logic
        if time.time() - last_time > CHECK_INTERVAL:
            print("📤 Sending frame...")
            send_frame(frame)
            last_time = time.time()

        # Display
        cv2.imshow('Visionary Agent', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()