#define DIR_1 13
#define STEP_1 12
#define SLEEP_1 14
#define RESET_1 14
#define MS3_1 27
#define MS2_1 26
#define MS1_1 25
#define ENABLE_1 33
#define steps_per_rev 200

#define DIR_2 15
#define STEP_2 4
#define SLEEP_2 16
#define RESET_2 16
#define MS3_2 17
#define MS2_2 5
#define MS1_2 18
#define ENABLE_2 19

void setup()
{
  Serial.begin(115200);

  // Setup for Motor 1
  pinMode(STEP_1, OUTPUT);
  pinMode(DIR_1, OUTPUT);
  digitalWrite(ENABLE_1, LOW);
  digitalWrite(SLEEP_1, LOW);
  digitalWrite(RESET_1, LOW);
  digitalWrite(MS1_1, LOW);
  digitalWrite(MS2_1, LOW);
  digitalWrite(MS3_1, LOW);

  // Setup for Motor 2
  pinMode(STEP_2, OUTPUT);
  pinMode(DIR_2, OUTPUT);
  digitalWrite(ENABLE_2, HIGH);
  digitalWrite(SLEEP_2, LOW);
  digitalWrite(RESET_2, LOW);
  digitalWrite(MS1_2, LOW);
  digitalWrite(MS2_2, LOW);
  digitalWrite(MS3_2, LOW);
}

void loop()
{
  digitalWrite(DIR_1, HIGH);
  Serial.println("Spinning Clockwise...");

  for (int i = 0; i < 200; i++)
  {
    digitalWrite(STEP_1, HIGH);
    delayMicroseconds(1000);
    digitalWrite(STEP_1, LOW);
    delayMicroseconds(1000);
  }

  digitalWrite(DIR_2, HIGH);
  Serial.println("Spinning Clockwise...");

  for (int i = 0; i < 200; i++)
  {
    digitalWrite(STEP_2, HIGH);
    delayMicroseconds(1000);
    digitalWrite(STEP_2, LOW);
    delayMicroseconds(1000);
  }
  delay(1000);

  /*digitalWrite(DIR_1, LOW);
  Serial.println("Spinning Anti-Clockwise...");

  for (int i = 0; i < steps_per_rev; i++)
  {
    digitalWrite(STEP_1, HIGH);
    delayMicroseconds(1000);
    digitalWrite(STEP_1, LOW);
    delayMicroseconds(1000);
  }
  delay(1000);*/
}