#ifndef THERMISTOR_H
#define THERMISTOR_H

#include <Ewma.h> // exponential filter

// http://mathscinotes.com/2011/07/thermistor-mathematics/ // thermistor
// https://github.com/jonnieZG/EWMA    // exponential filter
Ewma adcFilter2(0.05);


class Thermistor {
  public:
    Thermistor(int _pin ) {
      pin = _pin;
    }
    Thermistor() {
    }
    ~Thermistor() {}

    virtual float getValue() {
      filtered = adcFilter2.filter(analogRead(pin));
      return ThermistorFunction(filtered);
    }
    // http://mathscinotes.com/2011/07/thermistor-mathematics/
    virtual float ThermistorFunction(float aveADC) {
      float R1 = 4700.;   // This resistor is fixed on the RAMPS PCB.
      float Ro = 100000.; // This is from the thermistor spec sheet
      float beta = 3950.; // This is from the thermistor spec sheet
      float To = 298.15;     // This is from the thermistor spec sheet
      float R;
      float Temp;
      R  = R1 / ((1023. / aveADC) - 1.);
      Temp = 1 / ((1 / beta) * log(R / Ro) + 1 / To);
      Temp = Temp - 273.15;            // Convert Kelvin to Celcius
      return Temp; // deg C
    }


  private:
    int pin;
    float filtered;

};

#endif
