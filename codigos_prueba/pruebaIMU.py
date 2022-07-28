# Simple demo of the LSM303 accelerometer, magnetometer, L3GD20 gyroscope.
# Will print the acceleration, magnetometer, and gyroscope values every second.
import time
import board
import adafruit_lsm303dlh_mag
import adafruit_lsm303_accel
import adafruit_l3gd20

# Create sensor object, communicating over the board's default I2C bus
i2c = board.I2C()  # uses board.SCL and board.SDA
accel = adafruit_lsm303_accel.LSM303_Accel(i2c)
mag = adafruit_lsm303dlh_mag.LSM303DLH_Mag(i2c)

# default i2c_address = 0x6b ## chino i2c_address = 0x69
# default chip_id = 0xd4 o 0xd7 ## chino chip_id = 0xd3 (se modificó la biblioteca para agregar esta excepción)
gyro = adafruit_l3gd20.L3GD20_I2C(i2c,rng=adafruit_l3gd20.L3DS20_RANGE_250DPS, address=0x69)


# Main loop will read the acceleration, magnetometer, gyroscope
# values every second and print them out.
while True:
    # Read acceleration, magnetometer, gyroscope.
    accel_x, accel_y, accel_z = accel.acceleration
    mag_x, mag_y, mag_z = mag.magnetic
    gyro_x, gyro_y, gyro_z = gyro.gyro
    # Print values.
    print(
        "Acceleration (m/s^2): ({0:0.3f},{1:0.3f},{2:0.3f})".format(
            accel_x, accel_y, accel_z
        )
    )
    print(
        "Magnetometer (gauss): ({0:0.3f},{1:0.3f},{2:0.3f})".format(
            mag_x, mag_y, mag_z)
    )
    print(
        "Gyroscope (rad/sec): ({0:0.3f},{1:0.3f},{2:0.3f})".format(
            gyro_x, gyro_y, gyro_z
        )
    )
    # Delay for a second.
    time.sleep(1.0)

