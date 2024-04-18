mkdir -p configuration-images/retrieved-captures/
ssh camera@192.168.22.1 << CAPTURE_COMMANDS
  rpicam-jpeg -o /tmp/capture.jpg -t 0.1 --width 800 --height 800 --shutter 20000 --gain 20.0
CAPTURE_COMMANDS
scp camera@192.168.22.1:/tmp/capture.jpg ./camera-configuration/retrieved-captures/$1.jpg
feh ./camera-configuration/retrieved-captures/$1.jpg -ZF
