#include "Arduino.h"
#include "DRV8825.h"

#define MOTOR_STEPS 200

#define DIR_1 19
#define STEP_1 4
#define SLEEP_1 32
#define RESET_1 32

#define DIR_2 13
#define STEP_2 33
#define SLEEP_2 27
#define RESET_2 27

#define X_RATIO 8.0 // 128 for X gear and 16 for small gear
#define Y_RATIO 10.0 // 160 for COMET gear and 16 for small gear

#define LIMIT_SWITCH 34  // Pin for the limit switch (must be interrupt-capable)

enum commands 
{
  STOP = 0x00,
  RESET = 0x01,
  SET = 0x02,
  TRACK = 0x03,
  END = 0x04,
  TIME = 0x05,
  RESETSYSTEM = 0x06
};

DRV8825 stepper1(MOTOR_STEPS, DIR_1, STEP_1);
DRV8825 stepper2(MOTOR_STEPS, DIR_2, STEP_2);

// Variables to track the motor state
volatile bool stopMotors = false;
volatile bool limitSwitchPressed = false;  // To track if the switch is pressed or released

bool moveReverseX = false;
bool moveReverseY = false;

bool movingAlongX = false;
bool movingAlongY = false;

int stopY = 0;
int tracking = 0;
int initialSet = 0;
int endSet = 0;
int timeSet = 0;

float stepperXDegrees = 0.0;
float stepperYDegrees = 0.0;

float initialAzimuth = 0.0;
float initialElevation = 0.0;

float finalAzimuth = 0.0;
float finalElevation = 0.0;

float azimuthRate = 0.0;
float elevationRate = 0.0;

float timeDuration = 0.0;
float timeTracking = 0.0;

float pastTime = 0.0;
float currentTime = 0.0;
bool pastTimeTaken = false;

// Function to stop the motors
void stopAllMotors() {
  stepper1.stop();
  stepper2.stop();
  tracking = 0;
  initialSet = 0;
  endSet = 0;
  timeSet = 0;
  /*timeDuration = 0;
  initialAzimuth = 0.0;
  initialElevation = 0.0;
  finalAzimuth = 0.0;
  finalElevation = 0.0;*/
}

void handleMotorSwitchCase() {
  stepper2.stop();
  stopY = 1;
}

void resetAllMotors() {
  resetXMotor();
  resetYMotor();
}

void doTracking() {
  if (!pastTimeTaken) {
    pastTime = millis();
    pastTime /= 1000;
    pastTimeTaken = true;
  }

  currentTime = millis();
  currentTime /= 1000;

  float totalTimeElapsed = currentTime - pastTime;

  /*Serial.println(currentTime);
  Serial.println(pastTime);
  Serial.println(totalTimeElapsed);*/

  if (totalTimeElapsed >= 15.0) 
  {
    stepper1.rotate((azimuthRate) * totalTimeElapsed);
    stepperXDegrees += (azimuthRate) * totalTimeElapsed;

    stepper2.rotate((elevationRate) * totalTimeElapsed);
    stepperYDegrees += (elevationRate) * totalTimeElapsed;
    /*Serial.println(stepperXDegrees);
    Serial.println(stepperYDegrees);*/

    timeTracking += totalTimeElapsed;
    //Serial.println(timeTracking);

    pastTimeTaken = false;
  }

 if (timeTracking >= timeDuration)
 {
    tracking = 0;
    initialSet = 0;
    endSet = 0;
    timeSet = 0;
    timeDuration = 0;
    initialAzimuth = 0.0;
    initialElevation = 0.0;
    finalAzimuth = 0.0;
    finalElevation = 0.0;
 }
  
}

void setInitalMotors() {
  bool settingMotors = true;

    Serial.println("READY_TO_SET");
    while (Serial.available() == 0) {}
    String inputString = Serial.readStringUntil('\n');

    int commaIndex = inputString.indexOf(',');
    String strXAngle = inputString.substring(0, commaIndex);
    String strYAngle = inputString.substring(commaIndex + 1);
    
    float x_angle = strXAngle.toFloat();
    float y_angle = strYAngle.toFloat();

    /*Serial.println(x_angle);
    Serial.println(y_angle);*/
    
    setMotorX(x_angle * X_RATIO);
    setMotorY(y_angle * Y_RATIO);

    /*Serial.println(initialAzimuth);
    Serial.println(initialElevation);*/

    initialSet = 1;
}

void setEndMotors() {
  Serial.println("READY_TO_END");
  while (Serial.available() == 0) {}
  String inputString = Serial.readStringUntil('\n');

  int commaIndex = inputString.indexOf(',');
  String strXAngle = inputString.substring(0, commaIndex);
  String strYAngle = inputString.substring(commaIndex + 1);
  
  finalAzimuth = strXAngle.toFloat();
  finalElevation = strYAngle.toFloat();

  /*Serial.println(finalAzimuth);
  Serial.println(finalElevation);*/

  finalAzimuth *= X_RATIO;
  finalElevation *= Y_RATIO;

  /*Serial.println(finalAzimuth);
  Serial.println(finalElevation);*/

  endSet = 1;
}

void setTimeDuration() {
  Serial.println("READY_TO_TIME");
  while (Serial.available() == 0) {}
  String inputString = Serial.readStringUntil('\n');
  
  timeDuration = inputString.toFloat();

  //Serial.println(timeDuration);

  timeSet = 1;
}

void setMotorX(float newDegrees) {
  float delta = newDegrees - initialAzimuth;
  stepper1.rotate(delta);
  initialAzimuth = newDegrees;
  stepperXDegrees = newDegrees;
}

void setMotorY(float newDegrees) {
  float delta = newDegrees - initialElevation;
  stepper2.rotate(delta);
  initialElevation = newDegrees;
  stepperYDegrees = newDegrees;
}

void resetXMotor() {
  stepper1.rotate(-1 * stepperXDegrees);  // Rotate back to zero degrees
  stepperXDegrees = 0;
}

void resetYMotor() {
  stepper2.rotate(-1 * stepperYDegrees);  // Rotate back to zero degrees
  stepperYDegrees = 0;
}

void findDegreesRate() {
  azimuthRate = (finalAzimuth - initialAzimuth) / timeDuration;
  elevationRate = (finalElevation - initialElevation) / timeDuration;
  /*Serial.print(initialAzimuth);
  Serial.print(finalAzimuth);
  Serial.print(timeDuration);
  Serial.print(azimuthRate);
  Serial.print(initialElevation);
  Serial.print(finalElevation);
  Serial.print(timeDuration);
  Serial.print(elevationRate);*/
}

void setup() {
  Serial.begin(9600);

  // Initialize the stepper motors
  stepper1.begin(5, 1);  // 5 RPM and full step mode
  stepper2.begin(5, 1);

  digitalWrite(SLEEP_1, HIGH);
  digitalWrite(RESET_1, HIGH);

  digitalWrite(SLEEP_2, HIGH);
  digitalWrite(RESET_2, HIGH);

  // Set up limit switch as an input with internal pull-up resistor
  pinMode(LIMIT_SWITCH, INPUT);
}

void read_serial() {
  if (Serial.available()) {
    int command = Serial.parseInt();

    switch (command) {
      case STOP:
        stopAllMotors();
        stopY = 0;
        break;
      case RESET:
        resetAllMotors();
        break;
      case SET:
        setInitalMotors();
        break;
      case TRACK:
        if (initialSet == 1 && endSet == 1 && timeSet == 1) {
          findDegreesRate();
          tracking = 1;
        }
        break;
      case END:
        setEndMotors();
        break;
      case TIME:
        setTimeDuration();
        break;
      default:
       // Serial.println("Invalid Command, please enter a valid command.");
        break;
    }
  }
}

void loop() {
  // Handle incoming serial commands
  read_serial();

  if (digitalRead(LIMIT_SWITCH) == HIGH) {
    handleMotorSwitchCase();
  }

  // Perform tracking if enabled
  if (tracking == 1 && initialSet == 1 && endSet == 1 && timeSet == 1) {
    doTracking();
  }

  // Add a small delay to avoid flooding the serial output
  delay(100);
}