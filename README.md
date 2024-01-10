# PraktikumSAP

## A repository for our internship at SAP St. Ingbert

While our internship at SAP, we developed a programm that tracks your hand and gestures. With gestures for example you can print emojis. You can also see the skeleton overlayed on your hand and have a laser pointer.


## How does it work?
We are using a python package called "MediaPipe". It was developed by google and is
using AI recognition to detect hands, gestrues, objects and faces. We use it to detect your hand and which gestures you do. We then display it in a tkinter window which also manages the settings window.


## Available Gestures

### Quick chatting using emojis 
1. Thumbs up: if you show a thumbs up in your camera it writes the emoji "👍" and presses "Enter"

2. Thumbs down: if you show a thumbs down in your camera it writes the emoji "👎" and presses "Enter"



## Settings
### Entries
1. Detection Confidence: How sure the tracking needs to be to detect a hand.
    * Value range: 0 - 1
    * Value type: float
  
2. Tracking Confidence: How sure it needs to be that your hand is moving.
    * Value range: 0 - 1
    * Value type: float
  
3. Max Number of Hands: How many hands are tracked at the same time.
   * Value range: 1 - infinity
   * Value type: integer
  
4. Model Complexity: How accurate the tracking is.
   * Value range: 0 - 1
   * Value type: integer
   * Value meaning: 0 = better performance; 1 = more accurate, but more latency

5. Camera Number: The number of the camera you want to use.
   * Value range: starting from 0
   * Value type: float

### Checkboxes
1. Toggle skeleton mode:
   * On: Overlay the tracked skeleton over your hand
   * Off: Don't show the skeleton

2. Toggle laser pointer:
   * On: Show a laser pointer starting from the tip of your index finger that reaches the border of the screen
   * Off: Don't show the laser pointer

### Don't forget to apply your settings using the "Apply" button or the "Enter" key on your keyboard
