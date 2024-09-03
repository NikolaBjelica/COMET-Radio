#define DIR 13
#define STEP 12
#define SLEEP 14
#define RESET 14
#define MS3 27
#define MS2 26
#define MS1 25
#define ENABLE 33
#define steps_per_rev 200

void setup()
{
  Serial.begin(115200);
  pinMode(STEP, OUTPUT);
  pinMode(DIR, OUTPUT);
  digitalWrite(ENABLE, LOW);
  digitalWrite(SLEEP, LOW);
  digitalWrite(RESET, LOW);
  digitalWrite(MS1, LOW);
  digitalWrite(MS2, LOW);
  digitalWrite(MS3, LOW);
}

void loop()
{
  digitalWrite(DIR, HIGH);
  Serial.println("Spinning Clockwise...");

  for (int i = 0; i < 10; i++)
  {
    digitalWrite(STEP, HIGH);
    delayMicroseconds(100000);
    digitalWrite(STEP, LOW);
    delayMicroseconds(100000);
  }
  delay(1000);

  /*digitalWrite(DIR, LOW);
  Serial.println("Spinning Anti-Clockwise...");

  for (int i = 0; i < steps_per_rev; i++)
  {
    digitalWrite(STEP, HIGH);
    delayMicroseconds(1000);
    digitalWrite(STEP, LOW);
    delayMicroseconds(1000);
  }
  delay(1000);*/
}
