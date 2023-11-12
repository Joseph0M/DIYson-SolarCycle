from smbus2 import SMBus

with SMBus(1) as bus:
    data = [1, 2, 3, 4, 5, 6, 7, 8]
    bus.write_i2c_block_data(80, 0, data)

