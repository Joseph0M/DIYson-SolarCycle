config = {
    "SENSOR_DATA": {
        "TOF":{
            "MODEL": "VL53L0X",
            "I2C_BUS": 0,
            "ADDR": "0x29"
        },
        "ALS":{
            "MODEL": "LTR559",
            "I2C_BUS": 0,
            "ADDR": "0x23"
        },
        "PS":{
            "MODEL": "LTR559",
            "I2C_BUS": 0,
            "ADDR": "0x23"
        }
    },
    "HARDWARE": {
        "MODEL": "DIYSON",
        "WIFI": True,
        "I2C":{
            "0": {
                "SDA": 15,
                "SCL": 14
            },
            "1": {
                "SDA": 3,
                "SCL": 2
            }
        }
    }
}