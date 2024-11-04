#include "Arduino.h"
#include "DRV8825.h"

#define MOTOR_STEPS 200

#define DIR_1 19
#define STEP_1 4
#define SLEEP_1 32
#define RESET_1 32

#define DIR_2 13
#define STEP_2 14
#define SLEEP_2 27
#define RESET_2 27

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

float pastTime = 0.0;
float currentTime = 0.0;
bool pastTimeTaken = false;

// Function to stop the motors
void stopAllMotors() {
  stepper1.stop();
  stepper2.stop();
  Serial.println("Motors stopped.");
  tracking = 0;
  initialSet = 0;
  endSet = 0;
  timeDuration = 0;
  initialAzimuth = 0.0;
  initialElevation = 0.0;
  finalAzimuth = 0.0;
  finalElevation = 0.0;
}

void handleMotorSwitchCase() {
  stepper2.stop();
  stopY = 1;
  Serial.print(stopY);
  Serial.println("Y Motor hit the limit switch");
}

void resetAllMotors() {
  resetXMotor();
  resetYMotor();
  Serial.println("Both motors reset to initial positions.");
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

  if (totalTimeElapsed >= 15.0) {
    stepper1.rotate(azimuthRate * totalTimeElapsed);
    stepperXDegrees += azimuthRate * totalTimeElapsed;
    Serial.println(stepperXDegrees);

    stepper2.rotate(elevationRate * totalTimeElapsed);
    stepperYDegrees += elevationRate * totalTimeElapsed;
    Serial.println(stepperYDegrees);

    pastTimeTaken = false;
  }
}

void setInitalMotors() {
  bool settingMotors = true;

  while (settingMotors) {
    Serial.println("READY_TO_SET");
    while (Serial.available() == 0) {}
    String inputString = Serial.readStringUntil('\n');

    int commaIndex = inputString.indexOf(',');
    String strXAngle = inputString.substring(0, commaIndex);
    String strYAngle = inputString.substring(commaIndex + 1);
    
    float x_angle = strXAngle.parseFloat();
    float y_angle = strXAngle.parseFloat();

    Serial.println(x_angle);
    Serial.println(y_angle);

    unsigned long StartTime = millis();

    setMotorX(x_angle);
    setMotorY(y_angle);

    Serial.println("Satisfied?\n\r 0 for Yes\n\r 1 for No\n");
    while (Serial.available() == 0) {}
    int response = Serial.parseInt();

    if (0 == response) {
      settingMotors = false;
      initialSet = 1;
    }
  }
}

void setEndMotors() {
  Serial.println("What angle would you want to end for the X Motor?");
  while (Serial.available() == 0) {}
  finalAzimuth = Serial.parseFloat();

  Serial.println(finalAzimuth);

  Serial.println("What angle would you want to end for the Y Motor?");
  while (Serial.available() == 0) {}
  finalElevation = Serial.parseFloat();

  Serial.println(finalElevation);

  endSet = 1;
}

void setTimeDuration() {
  Serial.println("How long do you want the tracking to endure?");
  while (Serial.available() == 0) {}
  timeDuration = Serial.parseFloat();
  timeSet = 1;
}

void setMotorX(float newDegrees) {
  Serial.println("In here setMotorX");
  float delta = newDegrees - initialAzimuth;
  stepper1.rotate(delta);
  initialAzimuth = newDegrees;
  stepperXDegrees = newDegrees;
}

void setMotorY(float newDegrees) {
  Serial.println("In here setMotorY");
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
  Serial.println('\n');
  Serial.print(finalAzimuth);
  Serial.println('\n');
  Serial.print(timeDuration);
  Serial.println('\n');
  Serial.print(azimuthRate);
  Serial.println('\n');
  Serial.print(initialElevation);
  Serial.println('\n');
  Serial.print(finalElevation);
  Serial.println('\n');
  Serial.print(timeDuration);
  Serial.println('\n');
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
        } else
          Serial.println("Not all parameters have been set...");
        break;
      case END:
        setEndMotors();
        break;
      case TIME:
        setTimeDuration();
        break;
      default:
        Serial.println("Invalid Command, please enter a valid command.");
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
