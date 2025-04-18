from flask import Flask, Response
import cv2

app = Flask(__name__)

@app.route('/snapshot')
def snapshot():
    # Open the camera stream
    camera = cv2.VideoCapture(0)
    success, frame = camera.read()
    camera.release()  # Release the camera after capturing the frame

    if not success:
        # If the camera fails to capture a frame, return an error image or message
        return Response("Failed to capture snapshot", status=500)

    # Encode the captured frame as JPEG
    _, encoded_image = cv2.imencode('.jpg', frame)

    # Create the response with image data and proper headers to prevent caching
    response = Response(encoded_image.tobytes(), mimetype='image/jpeg')
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'  # Additional cache prevention
    response.headers['Expires'] = '0'       # Ensure the image is treated as expired
    return response

if __name__ == '__main__':
    # Run the Flask app, accessible from all network interfaces
    app.run(host="0.0.0.0", port=5000)