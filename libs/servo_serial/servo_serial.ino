#include <Servo.h>

Servo myservo;
char p = '-1';
char last_p = '-1';

void setup()
{
  //Connect servo motor to PWM pin 9
  myservo.attach(9);
  
  
  //Jig servo back and forth to prevent stuttering
  myservo.write(0);
  delay(500);
  myservo.write(45);
  delay(500);
  myservo.write(0);
  
  Serial.begin(9600);
}

void loop()
{
  delay(50);
  if (Serial.available())
  {
    p = Serial.read();
    if(p != last_p)
    {
      if (p == '0')
      {
        myservo.write(0);
        Serial.println("Open");
      }
      else if (p == '1')
      {
        myservo.write(90);
        Serial.println("Closed");
      }
      else if (p == 'q')
      {
        Serial.println("Shutter");
      }
      last_p = p;
    }
    delay(50);
  }
}
