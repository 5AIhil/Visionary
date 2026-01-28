import cv2
import google.generativeai as genai
import os
import time
from dotenv import load_dotenv

# 1. SETUP: Configure the API and Model
# Best practice: Load from a .env file, but you can hardcode it for testing
# os.environ["GOOGLE_API_KEY"] = "PASTE_YOUR_KEY_HERE" 

load_dotenv() # Loads GOOGLE_API_KEY from a .env file if present
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# We use Gemini 1.5 Flash because it is fast and cheap/free for this use case
model = genai.GenerativeModel('gemini-1.5-flash')

def analyze_frame(frame, prompt):
    """
    Sends a video frame to Gemini and returns the AI's text response.
    """
    print(f"🤖 AI Thinking... Prompt: '{prompt}'")
    
    # OpenCV uses BGR, but Gemini expects RGB. Convert it.
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Convert the numpy array (OpenCV image) to a PIL Image object
    from PIL import Image
    pil_image = Image.fromarray(img_rgb)
    
    try:
        # Generate content using the image and the text prompt
        response = model.generate_content([prompt, pil_image])
        return response.text
    except Exception as e:
        return f"Error: {e}"

def main():
    # 2. CONNECT: Open the Webcam (0 is usually the default laptop cam)
    # To use a CCTV stream, replace 0 with the RTSP URL (e.g., "rtsp://admin:pass@192.168.1.10...")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return

    print("✅ Camera connected.")
    print("Controls:\n  [SPACE] - Capture current frame and send to AI\n  [q] - Quit")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Display the live video feed
        cv2.imshow('Visionary - CCTV Feed', frame)

        key = cv2.waitKey(1) & 0xFF

        # 3. INTERACT: Press SPACE to simulate an "Event"
        if key == ord(' '): 
            # Define your test prompt here
            user_prompt = "Describe what you see in this image. Is there any person? If yes, what are they doing?"
            
            # Call the AI function
            analysis = analyze_frame(frame, user_prompt)
            
            print("-" * 40)
            print("GEMINI SAYS:")
            print(analysis)
            print("-" * 40)

        # Press 'q' to quit
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()