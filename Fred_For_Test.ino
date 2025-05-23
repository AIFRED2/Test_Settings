#include <math.h>
#include "Thermistor.h"
#include "pin_map.h"
#include <PID_v1.h>
#include <AccelStepper.h>

Thermistor Thermistor1(TEMP_0_PIN);
float Temp;
String input = "";
String digits = "0000";  // Estado de los actuadores

// Motores
AccelStepper motor1(AccelStepper::DRIVER, 54, 55); // Spool
AccelStepper motor2(AccelStepper::DRIVER, 26, 28); // Extruder
const int enablePin1 = 38;
const int enablePin2 = 24;
bool motor1Enabled = false;
bool motor2Enabled = false;

// PID
double Setpoint, Input, Output;
double Kp = 22.85, Ki = 1.85, Kd = 70.65;
PID myPID(&Input, &Output, &Setpoint, Kp, Ki, Kd, DIRECT);

// Estados
int moto_m = 0, fan_m = 0, heater_m = 0, extruder_m = 0;
unsigned long lastStatusUpdate = 0;

void setup() {
  Serial.begin(115200);
  Serial.println("Conexión establecida");

  pinMode(TEMP_0_PIN, INPUT_PULLUP);
  pinMode(RAMPS_D9_PIN, OUTPUT);    // fan
  pinMode(RAMPS_D10_PIN, OUTPUT);   // heater <-- lo agregamos
  pinMode(TEMP_OUT, OUTPUT);
  pinMode(enablePin1, OUTPUT);
  pinMode(enablePin2, OUTPUT);

  digitalWrite(enablePin1, HIGH);
  digitalWrite(enablePin2, HIGH);

  motor1.setMaxSpeed(5000);
  motor1.setAcceleration(100);

  motor2.setMaxSpeed(2000);
  motor2.setAcceleration(1000);

  Setpoint = 190;
  myPID.SetMode(AUTOMATIC);
  myPID.SetOutputLimits(0, 255);
}

void loop() {
  delay(10);
  Input = Thermistor1.getValue();
  myPID.Compute();

  // Procesar datos seriales
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      processInput(input);
      input = "";
    } else {
      input += c;
    }
  }

  // MOTOR SPOOL
  if (digits.length() >= 1 && digits[0] == '1') {
    if (!motor1Enabled) {
      digitalWrite(enablePin1, LOW);
      motor1Enabled = true;
    }
    motor1.setSpeed(500);
    motor1.runSpeed();
    moto_m = 1;
  } else {
    if (motor1Enabled) {
      digitalWrite(enablePin1, HIGH);
      motor1Enabled = false;
    }
    moto_m = 0;
  }

  // FAN
  if (digits.length() >= 2 && digits[1] == '1') {
    analogWrite(RAMPS_D9_PIN, 150);
    fan_m = 1;
  } else {
    analogWrite(RAMPS_D9_PIN, 0);
    fan_m = 0;
  }

  // EXTRUDER
  if (digits.length() >= 3 && digits[2] == '1') {
    if (!motor2Enabled) {
      digitalWrite(enablePin2, LOW);
      motor2Enabled = true;
    }
    motor2.runSpeed();
    extruder_m = 1;
  } else {
    if (motor2Enabled) {
      digitalWrite(enablePin2, HIGH);
      motor2Enabled = false;
    }
    extruder_m = 0;
  }

  // HEATER (control por PID + ACTUATE)
  // Solo aplica calor si el usuario lo encendió (digits[3]=='1')
  // y la temperatura actual está por debajo del setpoint.
  if (digits.length() >= 4 && digits[3] == '1' && Input < Setpoint) {
    analogWrite(RAMPS_D10_PIN, (int)Output);
    heater_m = 1;
  } else {
    analogWrite(RAMPS_D10_PIN, 0);
    heater_m = 0;
  }

  // Mostrar estado cada segundo
  unsigned long currentMillis = millis();
  if (currentMillis - lastStatusUpdate >= 1000) {
    lastStatusUpdate = currentMillis;
    Serial.print("Temp:"); 
    Serial.println(Input);
    Serial.println("--- Estado de componentes ---");
    Serial.print("Motor Spool: "); Serial.println(moto_m ? "Encendido" : "Apagado");
    Serial.print("Fan:          "); Serial.println(fan_m ? "Encendido" : "Apagado");
    Serial.print("Heater:       "); Serial.println(heater_m ? "Encendido" : "Apagado");
    Serial.print("Extruder:     "); Serial.println(extruder_m ? "Encendido" : "Apagado");
    Serial.println("-----------------------------");
  }
}

void processInput(String command) {
  Serial.print("Recibido: ");
  Serial.println(command);

  if (command.startsWith("ACTUATE:")) {
    digits = command.substring(8);
  } else if (command.startsWith("SPEED:")) {
    int nuevaVel = command.substring(6).toInt();
    motor2.setSpeed(nuevaVel);
    Serial.print("Nueva velocidad extrusor: ");
    Serial.println(nuevaVel);
  }
}
