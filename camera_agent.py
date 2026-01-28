import cv2
import time
import base64
import requests # Pip install requests if needed

# CONFIGURATION
API_URL = "http://localhost:8000/analyze"
CHECK_INTERVAL = 5  # Seconds between checks
# The prompt is hardcoded for now, but in Phase 3 we will make this dynamic
DEFAULT_PROMPT = "Is there a person in this frame? If yes, are they handsome? Answer simply Yes/No."

def send_frame_to_api(frame):
    # 1. Encode frame to Base64 string to send over network
    _, buffer = cv2.imencode('.jpg', frame)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')

    # 2. Prepare Payload
    payload = {
        "image_base64": jpg_as_text,
        "prompt": DEFAULT_PROMPT
    }

    # 3. Send to Backend
    try:
        response = requests.post(API_URL, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ AI Response: {data['ai_response']}")
            
        elif response.status_code == 500:
            # If server crashes (likely due to quota), print simpler error
            print(f"⏳ Quota Hit (500). Waiting for cool-down...")
            
        else:
            print(f"❌ Server Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

def main():
    cap = cv2.VideoCapture(0)
    last_check_time = time.time()

    print(f"📷 Agent started. Monitoring every {CHECK_INTERVAL} seconds...")

    while True:
        ret, frame = cap.read()
        if not ret: break

        # Draw a timer on screen so you know when the next check is
        time_diff = time.time() - last_check_time
        if time_diff >= CHECK_INTERVAL:
            print("Sending frame for analysis...")
            send_frame_to_api(frame)
            last_check_time = time.time()

        # Display feed
        cv2.putText(frame, f"Next Scan: {int(CHECK_INTERVAL - time_diff)}s", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow('Visionary Agent', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()