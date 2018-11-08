import copy, sys
import numpy as np
from ctapipe.io import event_source
from ctapipe.calib import CameraCalibrator
from ctapipe.image import tailcuts_clean

import vtk

tail_cut = {"LSTCam": (5, 10),
            "NectarCam": (7, 14),
            "FlashCam": (7, 14),
            "SCTCam": (5, 10),
            "CHEC": (3, 6),
            "DigiCam": (3, 6),
            "ASTRICam": (5, 10)}

# LOAD AND CALIBRATE

pwd = "/home/thomas/Programs/astro/CTAPIPE_DAN/"
# filename = 'gamma_20deg_0deg_run100___cta-prod3-lapalma3-2147m-LaPalma_cone10.simtel.gz'
filename = 'gamma_20deg_0deg_run100___cta-prod3_desert-2150m-Paranal-merged.simtel.gz'
# filename = 'gamma_20deg_0deg_run118___cta-prod3_desert-2150m-Paranal-merged_cone10.simtel.gz'
# filename = 'gamma_20deg_180deg_run11___cta-prod3_desert-2150m-Paranal-merged_cone10.simtel.gz'

# layout = np.loadtxt(pwd+'CTA.prod3Sb.3HB9-FG.lis', usecols=0, dtype=int)

filename = pwd + filename
if "Paranal" in filename:
    layout = [4, 5, 6, 11]
    print("PARANAL WITH {0}".format(layout))
elif "palma" in filename:
    layout = [5, 6, 7, 8]
    print("LAPALMA WITH {0}".format(layout))

print("Layout telescopes IDs:".format(layout))

# layout = [279, 280, 281, 282, 283, 284, 286, 287, 289, 297, 298, 299,
#           300, 301, 302, 303, 304, 305, 306, 307, 308, 315, 316, 317,
#           318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329,
#           330, 331, 332, 333, 334, 335, 336, 337, 338, 345, 346, 347,
#           348, 349, 350, 375, 376, 377, 378, 379, 380, 393, 400, 402,
#           403, 404, 405, 406, 408, 410, 411, 412, 413, 414, 415, 416,
#           417]

layout = set(layout)

source = event_source(filename)
source.max_events = 50
source.allowed_tels = layout
events = [copy.deepcopy(event) for event in source]

cal = CameraCalibrator(None, None, r1_product='HESSIOR1Calibrator', extractor_product='NeighbourPeakIntegrator')
for event in events:
    cal.calibrate(event)

# Find "big" event (piece of code from T.V. notebook ...thanks :D )
events_amplitude = []
for event in events:
    event_amplitude = 0
    for tel_id in event.r0.tels_with_data:
        if event.dl1.tel[tel_id].image is not None:
            event_amplitude += event.dl1.tel[tel_id].image[0].sum()
    events_amplitude.append(event_amplitude)
events_amplitude = np.array(events_amplitude)

mm = events_amplitude.argmax()
print("event: {0}".format(mm))
event = events[mm]

subinfo = event.inst.subarray
itel = list(event.r0.tels_with_data)

id_tel = itel[0]

camera = subinfo.tel[id_tel].camera

x_px = camera.pix_x.value
y_px = camera.pix_y.value


# Perform tailcut cleaning on image
pic_th = tail_cut[camera.cam_id][0]
bound_th = tail_cut[camera.cam_id][1]
image_cal = event.dl1.tel[id_tel ].image[0]

mask_tail = tailcuts_clean(camera, image_cal,
                           picture_thresh=pic_th,
                           boundary_thresh=bound_th,
                           min_number_picture_neighbors=1)

max_col = np.max(image_cal*mask_tail)


# create a rendering window and renderer
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
WIDTH = 640
HEIGHT = 480
renWin.SetSize(WIDTH, HEIGHT)

# create a renderwindowinteractor
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

for i in range(len(x_px)):
    # create Cylinder
    cylinder = vtk.vtkCylinderSource()
    cylinder.SetResolution(6)
    cylinder.SetRadius(0.028)
    cylinder.SetHeight(0.5)

    # create a transform that rotates the cone
    transform = vtk.vtkTransform()
    transformFilter = vtk.vtkTransformPolyDataFilter()

    transform.Translate(x_px[i], y_px[i], 0)
    transform.RotateWXYZ(90, 1, 0, 0)
    transform.RotateY(100.8+30)
    transformFilter.SetTransform(transform)
    transformFilter.SetInputConnection(cylinder.GetOutputPort())
    transformFilter.Update()

    # mapper for the rotated cylinder
    coneMapper = vtk.vtkPolyDataMapper()
    coneMapper.SetInputConnection(transformFilter.GetOutputPort())

    # actor for rotated cone
    actor = vtk.vtkActor()
    actor.SetMapper(coneMapper)

    # apply color
    actor.GetProperty().SetColor(0, 0, 1)  # (R,G,B)

    # assign actor to the renderer
    ren.AddActor(actor)

camera = vtk.vtkCylinderSource()
camera.SetResolution(4)
camera.SetRadius(1.0)
camera.SetHeight(0.45)
camera.Update()

cameraMapper = vtk.vtkPolyDataMapper()
cameraMapper.SetInputConnection(camera.GetOutputPort())
cameraActor = vtk.vtkActor()
cameraActor.SetMapper(cameraMapper)
cameraActor.GetProperty().SetColor(0.3, 0.3, 0.3)  # 70% gray camera_folder
ren.AddActor(cameraActor)

ren.SetBackground(1., 1., 1.)  # Background color dark red

# enable user interface interactor
iren.Initialize()
renWin.Render()
iren.Start()