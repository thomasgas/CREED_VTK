#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vtk
import copy, sys
import numpy as np
from ctapipe.io import event_source
from ctapipe.calib import CameraCalibrator
from ctapipe.image import tailcuts_clean
import matplotlib.pyplot as plt

tail_cut = {"LSTCam": (10, 20),
            "NectarCam": (7, 14),
            "FlashCam": (7, 14),
            "SCTCam": (5, 10),
            "CHEC": (3, 6),
            "DigiCam": (3, 6),
            "ASTRICam": (5, 10)}

def MakeLUTFromCTF(data_camera):
    """
    Use a color transfer Function to generate the colors in the lookup table.
    See: http://www.vtk.org/doc/nightly/html/classvtkColorTransferFunction.html
    :param: tableSize - The table size
    :return: The lookup table.
    """

    max_col = np.max(data_camera)
    tableSize = data_camera.shape[0]

    ctf = vtk.vtkColorTransferFunction()
    ctf.SetColorSpaceToDiverging()
    # Green to tan.
    ctf.AddRGBPoint(0.0, 0.0, 0.0, 1.0)
    ctf.AddRGBPoint(0.5, 0.0, 1.0, 0.0)
    ctf.AddRGBPoint(1.0, 1.0, 0.0, 0.0)

    lut = vtk.vtkLookupTable()
    lut.SetNumberOfTableValues(tableSize)
    lut.Build()

    for i in range(tableSize):
        rgb = list(ctf.GetColor(data_camera[i] / max_col)) + [1]
        lut.SetTableValue(i, rgb)

    return lut

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
#event = events[0]

subinfo = event.inst.subarray
itel = list(event.r0.tels_with_data)

tel_id = itel[0]


camera = subinfo.tel[tel_id].camera

x_px = camera.pix_x.value
y_px = camera.pix_y.value

# Perform tailcut cleaning on image
pic_th = tail_cut[camera.cam_id][0]
bound_th = tail_cut[camera.cam_id][1]
image_cal = event.dl1.tel[tel_id].image[0]

mask_tail = tailcuts_clean(camera, image_cal,
                           picture_thresh=pic_th,
                           boundary_thresh=bound_th,
                           min_number_picture_neighbors=2)

cleaned = image_cal
cleaned[~mask_tail] = 0

# fig = plt.figure(figsize=(6, 6))
# plt.scatter(x_px, y_px, c=cleaned)
# plt.show()

tableSize = image_cal.shape[0]

lut = MakeLUTFromCTF(cleaned)


points = vtk.vtkPoints()
colors = vtk.vtkUnsignedCharArray()
colors.SetNumberOfComponents(3)

for i in range(len(x_px)):
    points.InsertNextPoint(x_px[i], y_px[i], 0)
    rgb = [0.0, 0.0, 0.0]
    lut.GetColor(float(i) / (tableSize - 1), rgb)
    ucrgb = list(map(int, [x * 255 for x in rgb]))
    colors.InsertNextTuple3(ucrgb[0], ucrgb[1], ucrgb[2])

polydata = vtk.vtkPolyData()
polydata.SetPoints(points)

colors.SetNumberOfTuples(polydata.GetNumberOfPoints())
polydata.GetPointData().SetScalars(colors)

# # Now, let's control normal on each point composing or 'fake' surface
# # We should say, let's give a direction to each point, a normal in strange for a point.
# pointNormalsArray = vtkDoubleArray()
# pointNormalsArray.SetNumberOfComponents(3)
# pointNormalsArray.SetNumberOfTuples(polydata.GetNumberOfPoints())
#
# pN1 = [0.0, 1.0, 1.0]
# pN2 = [0.0, 1.0, 1.0]
# pN3 = [0.0, 1.0, 1.0]
#
# pointNormalsArray.SetTuple(0, pN1)
# pointNormalsArray.SetTuple(1, pN2)
# pointNormalsArray.SetTuple(2, pN3)
#
# polydata.GetPointData().SetNormals(pointNormalsArray)

pixel_source = vtk.vtkCylinderSource()

pixel_source.SetResolution(6)
pixel_source.SetRadius(0.026)
pixel_source.SetHeight(0.5)
pixel_source.Update()

transform = vtk.vtkTransform()
transform.RotateWXYZ(90, 1, 0, 0)
transform.RotateY(100.8+30)
#
transformFilter = vtk.vtkTransformPolyDataFilter()
transformFilter.SetTransform(transform)
transformFilter.SetInputConnection(pixel_source.GetOutputPort())
transformFilter.Update()

glyph = vtk.vtkGlyph3D()

glyph.SetInputData(polydata)
glyph.SetSourceConnection(transformFilter.GetOutputPort())
glyph.SetColorModeToColorByScalar()
glyph.SetVectorModeToUseNormal()
glyph.ScalingOff()
glyph.Update()

mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(glyph.GetOutputPort())

actor = vtk.vtkActor()
actor.SetMapper(mapper)


WIDTH = 640
HEIGHT = 480

ren = vtk.vtkRenderer()
ren.SetBackground(0.7, 0.7, 0.7)
ren.AddActor(actor)

renwin = vtk.vtkRenderWindow()
renwin.AddRenderer(ren)
renwin.SetSize(WIDTH, HEIGHT)
iren = vtk.vtkRenderWindowInteractor()
iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
iren.SetRenderWindow(renwin)

renwin.Render()
iren.Initialize()
renwin.Render()
iren.Start()