from pickle import FALSE, TRUE
import sys
sys.path.append('../../../')

from DCAM550.API.Vzense_api_550 import *
import cv2
import time
import ctypes

camera = VzenseTofCam()


camera_count = camera.Ps2_GetDeviceCount()
retry_count = 100
while camera_count==0 and retry_count > 0:
    retry_count = retry_count-1
    camera_count = camera.Ps2_GetDeviceCount()
    time.sleep(1)
    print("scaning......   ",retry_count)

device_info=PsDeviceInfo()

if camera_count > 1:
    ret,device_infolist=camera.Ps2_GetDeviceListInfo(camera_count)
    if ret==0:
        device_info = device_infolist[0]
        for info in device_infolist: 
            print('cam uri:  ' + str(info.uri))
    else:
        print(' failed:' + ret)  
        exit()  
elif camera_count == 1:
    ret,device_info=camera.Ps2_GetDeviceInfo()
    if ret==0:
        print('cam uri:' + str(device_info.uri))
    else:
        print(' failed:' + ret)   
        exit() 
else: 
    print("there are no camera found")
    exit()

print("uri: "+str(device_info.uri))
ret = camera.Ps2_OpenDevice(device_info.uri)

if ret == 0:
    ret = camera.Ps2_StartStream()
    if ret == 0:
        print("start stream successful")
    else: print("Failed")

    ret, depthrange = camera.Ps2_GetDepthRange()
    if ret == 0:
        print("Ps2_GetDepthRange:", depthrange.value)
    else:
        print("Ps2_GetDepthRange failed:",ret)

    ret, depth_max, value_min, value_max = camera.Ps2_GetMeasuringRange(PsDepthRange(depthrange.value))
    if  ret == 0:
        print("Ps2_GetMeasuringRange: ",depth_max,",",value_min,",",value_max)
    else:
        print("Ps2_GetMeasuringRange failed:",ret)

    try:
        f = open("output", "wb")
        while True:
            ret, frameready = camera.Ps2_ReadNextFrame()
            if ret != 0:
                print("Ps2_ReadNextFrame failed:", ret)
                time.sleep(1)
                continue
        
            if  frameready.depth:      
                ret,depthframe = camera.Ps2_GetFrame(PsFrameType.PsDepthFrame)
                
                if  ret == 0:
                    frametmp = numpy.ctypeslib.as_array(depthframe.pFrameData, (1, depthframe.width * depthframe.height * 2))
                    f.write(frametmp.tobytes())
                    frametmp.dtype = numpy.uint16
                    frametmp.shape = (depthframe.height, depthframe.width)

                    #convert ushort value to 0xff is just for display
                    img = numpy.int32(frametmp)
                    img = img*255/5000
                    img = numpy.clip(img, 0, 255)
                    img = numpy.uint8(img)
                    cv2.imshow("Depth Image", img)
                else:
                    print("---end---")
            if  frameready.ir:
                ret,irframe = camera.Ps2_GetFrame(PsFrameType.PsIRFrame)
                if  ret == 0:
                    frametmp = numpy.ctypeslib.as_array(irframe.pFrameData, (1, irframe.width * irframe.height * 2))
                    frametmp.dtype = numpy.uint16
                    frametmp.shape = (irframe.height, irframe.width)
                    img = numpy.int32(frametmp)
                    img = img*255/3840
                    img = numpy.clip(img, 0, 255)
                    frametmp = numpy.uint8(img)
                    cv2.imshow("IR Image", frametmp)
            
            cv2.waitKey(1)

            print("depth range")
            for index, element in enumerate(PsDepthRange):
                print(index, element)
            mode_input = 5
            for index, element in enumerate(PsDepthRange):
                if  index == int(mode_input):
                    ret = camera.Ps2_SetDepthRange(element)
                    if  ret == 0:
                        print("Ps2_SetDepthRange {} success".format(element))
                        ret, depth_max, value_min, value_max = camera.Ps2_GetMeasuringRange(PsDepthRange(element))
                        if  ret == 0:
                            print(PsDepthRange(element)," Ps2_GetMeasuringRange: ",depth_max,",",value_min,",",value_max)
                        else:
                            print(PsDepthRange(element)," Ps2_GetMeasuringRange failed:",ret)

                    else:
                        print("Ps2_SetDepthRange {} failed {}".format(element,ret))


    except Exception as e:
            print(e)
    finally:
            print('end')
            f.close()
else:
    print('Ps2_OpenDevice failed: ' + str(ret))   
 
