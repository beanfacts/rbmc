nice -n 15 mjpg_streamer -i "input_uvc.so -r 720x576 -d /dev/video0" -o "output_http.so -p 7070 -w ./www"