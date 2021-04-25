# Rubik's Cube Solver on Raspberry Pi with Lego PoweredUp Hub

## Hardware

- Raspberry Pi Model 3 A+
- Legos (PoweredUp)
- LCD display with I2C adpater

[![Robot](/images/robot.png)](https://mecabricks.com/en/models/9P2k1Aoevon)

## Software installation

### Raspbian
```
sudo apt-get update
sudo apt-get upgrade
```

### OpenCV
```
sudo apt-get install python3-opencv
```

### BrickNil
```
sudo apt-get install python3-pip
sudo pip3 install bricknil
```

### LCDDriver
```
sudo apt-get install git python3-smbus
git clone https://github.com/the-raspberry-pi-guy/lcd
```

### PiCamera
```
sudo apt-get install python3-picamera
```

### Kociemba
```
sudo pip3 install kociemba
```

### rubiks-cube-tracker
```
sudo apt-get install python-pip python-opencv
sudo pip install git+https://github.com/dwalton76/rubiks-cube-tracker.git
```

### rubiks-color-resolver
```
sudo pip3 install git+https://github.com/dwalton76/rubiks-color-resolver.git
```

## Raspberry Configuration

Configure:
- Hostname
- Wifi 
- PiCamera
- I2C 
With the Raspberry configuration tool:
```
sudo raspi-config
```
