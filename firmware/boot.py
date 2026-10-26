# firmware/boot.py
# Secuencia de arranque del microcontrolador ESP32
import gc
import esp

# Desactivar depuración por defecto del SO de Espressif para salida limpia
esp.osdebug(None)

# Recolección inicial de memoria
gc.collect()

print("[Narval ESP32] Boot sequence completed. Initial free heap:", gc.mem_free(), "bytes.")
