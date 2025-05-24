import sys
import serial
import serial.tools.list_ports
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider, QFileDialog
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# -----------------------
# Serial: auto-detect puerto
# -----------------------

def encontrar_puerto_arduino():
    puertos = serial.tools.list_ports.comports()
    for p in puertos:
        if "Arduino" in p.description or "ttyACM" in p.device or "ttyUSB" in p.device:
            return p.device
    return None

puerto = encontrar_puerto_arduino() or "/dev/ttyACM0"
arduino = serial.Serial(puerto, 115200, timeout=1)

# -----------------------
# PlotCanvas: contenedor de gráficas
# -----------------------
class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=2, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)

    def plot(self, data, ylabel=""):
        self.axes.cla()
        self.axes.plot(data, linestyle='-')  # siempre línea continua
        if ylabel:
            self.axes.set_ylabel(ylabel)
        self.axes.grid(True)
        self.draw()

# -----------------------
# GUI principal
# -----------------------
class ControlGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI-FrED0 Control Interface")
        self.setWindowIcon(QIcon(r"tec-logo.png"))
        self.resize(900, 600)

        # Estados y datos
        self.estado = ['0','0','0','0']
        self.velocidad_extrusor = 100
        self.temp_data     = []        # lecturas de temperatura
        self.motor_data    = []        # 1/0 motor spool
        self.fan_data      = []        # 1/0 fan
        self.extruder_data = []        # 1/0 extrusor

        # Layout principal: izquierda (gráficas) / derecha (controles)
        main_layout = QHBoxLayout(self)

        # --- Panel de gráficas ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        self.canvas_temp     = PlotCanvas(self, width=5, height=2)
        self.canvas_motor    = PlotCanvas(self, width=5, height=2)
        self.canvas_fan      = PlotCanvas(self, width=5, height=2)
        self.canvas_extruder = PlotCanvas(self, width=5, height=2)
        left_layout.addWidget(self.canvas_temp)
        left_layout.addWidget(self.canvas_motor)
        left_layout.addWidget(self.canvas_fan)
        left_layout.addWidget(self.canvas_extruder)
        main_layout.addWidget(left_widget, 3)

        # --- Panel de controles ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Botones ON/OFF
        self.btn_spool   = QPushButton("Motor Spool (OFF)")
        self.btn_fan     = QPushButton("Fan (OFF)")
        self.btn_extrude = QPushButton("Extrusor (OFF)")
        self.btn_heater  = QPushButton("Heater (OFF)")
        for idx, btn, name in [
            (0, self.btn_spool,   "Motor Spool"),
            (1, self.btn_fan,     "Fan"),
            (2, self.btn_extrude, "Extrusor"),
            (3, self.btn_heater,  "Heater")
        ]:
            btn.clicked.connect(lambda ch, i=idx, b=btn, n=name: self.toggle(i, b, n))
            right_layout.addWidget(btn)

        # --- BOTÓN DE CONTROL DEL SERVO ---
        self.btn_servo = QPushButton("Iniciar Movimiento Servo")
        self.btn_servo.setCheckable(True)
        self.btn_servo.clicked.connect(self.toggle_servo)
        right_layout.addWidget(self.btn_servo)

        # Slider de velocidad de extrusor
        self.lbl_slider = QLabel(f"Velocidad Extrusor: {self.velocidad_extrusor}")
        self.slider     = QSlider(Qt.Horizontal)
        self.slider.setRange(10, 100)
        self.slider.setValue(self.velocidad_extrusor)
        self.slider.valueChanged.connect(self.actualizar_velocidad)
        right_layout.addWidget(self.lbl_slider)
        right_layout.addWidget(self.slider)

        # Botón exportar CSV
        self.export_button = QPushButton("Exportar CSV")
        self.export_button.clicked.connect(self.export_csv)
        right_layout.addWidget(self.export_button)

        right_layout.addStretch()
        main_layout.addWidget(right_widget, 1)

        # Timer para actualización periódica
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar)
        self.timer.start(500)   # cada 500 ms

    #------------------------------------------------
    # Funciones de control
    #------------------------------------------------
    def toggle(self, index, boton, nombre):
        self.estado[index] = '1' if self.estado[index]=='0' else '0'
        estado_txt = "ON" if self.estado[index]=='1' else "OFF"
        boton.setText(f"{nombre} ({estado_txt})")

    def actualizar_velocidad(self, val):
        self.velocidad_extrusor = val
        self.lbl_slider.setText(f"Velocidad Extrusor: {val}")

    def toggle_servo(self):
        if self.btn_servo.isChecked():
            self.btn_servo.setText("Detener Movimiento Servo")
            arduino.write(b"SERVO:ON\n")
        else:
            self.btn_servo.setText("Iniciar Movimiento Servo")
            arduino.write(b"SERVO:OFF\n")

    #------------------------------------------------
    # Loop de comunicación y gráfica
    #------------------------------------------------
    def actualizar(self):
        # 1) Enviar comandos de actuadores
        cmd_act = "ACTUATE:" + ''.join(self.estado) + "\n"
        arduino.write(cmd_act.encode())
        cmd_vel = f"SPEED:{self.velocidad_extrusor}\n"
        arduino.write(cmd_vel.encode())

        # 2) Leer todas las líneas serial disponibles
        while arduino.in_waiting:
            line = arduino.readline().decode(errors='ignore').strip()
            # Parseo de datos
            if line.startswith("Temp:"):
                try:
                    t = float(line.split(':')[1])
                    self.temp_data.append(t)
                except:
                    pass
            elif line.startswith("Motor Spool:"):
                v = 1 if "Encendido" in line else 0
                self.motor_data.append(v)
            elif line.startswith("Fan:"):
                v = 1 if "Encendido" in line else 0
                self.fan_data.append(v)
            elif line.startswith("Extruder:"):
                v = 1 if "Encendido" in line else 0
                self.extruder_data.append(v)

        # 3) Limitar largo de datos (últimos 100)
        max_len = 100
        self.temp_data     = self.temp_data[-max_len:]
        self.motor_data    = self.motor_data[-max_len:]
        self.fan_data      = self.fan_data[-max_len:]
        self.extruder_data = self.extruder_data[-max_len:]

        # 4) Actualizar gráficas
        self.canvas_temp.plot(self.temp_data, ylabel="Temp (°C)")
        self.canvas_motor.plot(self.motor_data, ylabel="Motor ON/OFF")
        self.canvas_fan.plot(self.fan_data, ylabel="Fan ON/OFF")
        self.canvas_extruder.plot(self.extruder_data, ylabel="Extrusor ON/OFF")

    #------------------------------------------------
    # Exportar CSV
    #------------------------------------------------
    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Guardar CSV", "data.csv", "CSV Files (*.csv)")
        if not path:
            return
        import csv
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['index','Temp','Motor','Fan','Extrusor'])
            for i in range(len(self.temp_data)):
                m = self.motor_data[i] if i < len(self.motor_data) else ''
                f_ = self.fan_data[i]    if i < len(self.fan_data)   else ''
                e = self.extruder_data[i] if i < len(self.extruder_data) else ''
                writer.writerow([i, self.temp_data[i], m, f_, e])
        print(f"CSV guardado en {path}")

# -----------------------
# Inicio de la aplicación
# -----------------------
def main():
    app = QApplication(sys.argv)
    gui = ControlGUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
