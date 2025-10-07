# AIFRED2 Test Suite
Pip install : pip install pyserial numpy pyqt5 pyqt5-qt5 pyqt5-sip matplotlib

¡Buen día!  
Este repositorio te permite poner a prueba **AIFRED2** en tu Raspberry Pi sin necesidad de conexión a Internet, ideal para tests sencillos.

---

## 📝 Descripción

AIFRED2 Test Suite incluye todo lo necesario para:

- Programar tu **Arduino Mega** con los librerías requeridas.  
- Ejecutar la interfaz de Python paso a paso en **Thonny**.  
- Verificar conexiones y funcionamiento en modo **offline**.

---

## 🚀 Prerrequisitos

- **Raspberry Pi OS Desktop** (incluye Thonny IDE).  
- **Arduino Mega** y cable USB.  
- Navegador web para descargar el repositorio de pruebas.

---

## ⚙️ Instalación de dependencias

Abre una terminal en tu Raspberry Pi y ejecuta:

```bash
sudo apt update && \
sudo apt install -y arduino python3-matplotlib

```
- arduino — IDE oficial para programar tu placa.
- python3-matplotlib — Biblioteca para generar gráficas en Python.

## 📥 Descargar Test Settings
En tu Raspberry Pi, abre el navegador y ve al repositorio AIFRED2 Test_Settings.

Descarga el ZIP y extrae su contenido en la carpeta de tu elección.

##🔌 Programación del Arduino Mega
Abre el IDE de Arduino.

Ve a tu codigo de Arduino → Add new tab  → ponle el mismo nombre de las librerias siguientes y copia y pega el contendio en el que corresponda:

- thermistor.h

- pin_map.h

En Herramientas → Placa, selecciona Arduino Mega 2560.

Conecta tu placa por USB y sube el sketch.

## ▶️ Ejecutar la interfaz en Thonny
Abre Thonny (Menú → Programación → Thonny Python IDE).

Carga el archivo Interface.py.

Haz clic en Run o ejecuta paso a paso para monitorear la salida.

## ✅ Verificación
Al completar estos pasos, tu AIFRED2 estará listo para pruebas offline. Comprueba que:

El Arduino envía datos correctamente.

Las gráficas en Matplotlib se despliegan sin errores.

La interfaz responde según lo esperado.


¡Gracias por usar AIFRED2 Test Suite!
