# USAGE
# python detect_barcode.py
# python detect_barcode.py --video video/video_games.mov

# import the necessary packages
import barcode_detection
from imutils.video import VideoStream
import argparse
import time
import cv2
from pyzbar import pyzbar
import imutils
from multiprocessing import Process, Queue
from multiprocessing import Pool, freeze_support, cpu_count
# construct the argument parse and parse the arguments

real_time = time.time()
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help="path to the (optional) video file")
ap.add_argument("-p", "--procs", type=int, default=-1, help="# of processes to spin up")
args = vars(ap.parse_args())

process = args["procs"] if args["procs"] > 0 else cpu_count()
#args['video'] = 'video\\video_games.mov'
# if the video path was not supplied, grab the reference to the
# camera





if not args.get("video", False):
	vs = VideoStream(src=0).start()
	time.sleep(2.0)

# otherwise, load the video
else:
	vs = cv2.VideoCapture(args["video"])

# keep looping over the frames
# so, convert them from float to integer.
frame_width = int(vs.get(3))
frame_height = int(vs.get(4))
size = (frame_width, frame_height)
result = cv2.VideoWriter('result.avi', 
                         cv2.VideoWriter_fourcc('M','J','P','G'),
                         30, size)


def detect_in_frame(frame):
	
 
	# check to see if we have reached the end of the
	# video

	# detect the barcode in the image
	box = barcode_detection.detect(frame)
	frame_clone = imutils.resize(frame.copy(), width=400)
	
	
	barcodes = pyzbar.decode(frame_clone)
	for barcode in barcodes:
		(x, y, w, h) = barcode.rect
		barcodeData = barcode.data.decode("utf-8")
		barcodeType = barcode.type
		text = "{} ({})".format(barcodeData, barcodeType)
		print(text)
		cv2.putText(frame, text, (x, y - 10),
			cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
		
	# if a barcode was found, draw a bounding box on the frame
	if box is not None:
		cv2.drawContours(frame, [box], -1, (0, 255, 0), 2)
	
	return frame

def poolCallback(returnDataFromPool):
    global results
    result.write(returnDataFromPool)

if __name__ == "__main__":
	freeze_support()
	start = time.time()
	p = Pool(process)
	while True:
		# grab the current frame and then handle if the frame is returned
		# from either the 'VideoCapture' or 'VideoStream' object,
		# respectively

		frame = vs.read()
		frame = frame[1] if args.get("video", False) else frame
		if frame is None:
			break
		
		p.apply_async(detect_in_frame, args=(frame,), callback=poolCallback)

	p.close()
	p.join()


	vs.release()

	result.release()



	# close all windows
	cv2.destroyAllWindows()
	end = time.time()
	
	end_real_time = time.time()
	print("CPU Time: {} seconds".format(end - start))
	print("Real Time {} seconds".format(end_real_time - real_time))