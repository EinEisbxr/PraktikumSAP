# Optimal setting values

## Confidences

* Detection Confidence: Use a higher value, like 0.8, if you want to make sure you are not detecting for example faces as hands. With lower values, like 0.5, the tracking often detects other parts of your body as your hand.

* Tracking Confidence: With a higher value, like 0.7, you get a tracking that is really exact, but sometimes cant track your hand in akward positions. A bit of jiggle is introduced with a lower value, like 0.4.

## Complexity

* Model Complexity: You can gain more performance by using 0, but the model complexity 1 is more accurate.
