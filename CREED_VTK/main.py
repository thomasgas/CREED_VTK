import copy
import vtk
import numpy as np
# from ctapipe.io import event_source
# from ctapipe.calib import CameraCalibrator
# from ctapipe.image import tailcuts_clean

from .camera.camera_file import camera_frame, camera_structure
from .utils.arrows import arrow_2d
from .telescope.LST import LST_create_mirror_plane, LST_tel_structure


tail_cut = {"LSTCam": (10, 20),
            "NectarCam": (7, 14),
            "FlashCam": (7, 14),
            "SCTCam": (5, 10),
            "CHEC": (3, 6),
            "DigiCam": (3, 6),
            "ASTRICam": (5, 10)}


class CREED_VTK:
    def __init__(self, event):
        self.event = event
        self.tel_ids = list(event.r0.tels_with_data)
        self.tel_id = {}
        self.tel_coords = event.inst.subarray.tel_coords
        self.ren = vtk.vtkRenderer()
        self.ren.SetBackground(0.8, 0.8, 0.8)
        self.pointing = {}

        for id_tel in self.tel_ids:
            self.tel_id[id_tel] = []
            self.pointing[id_tel] = {'alt': np.rad2deg(event.mc.tel[id_tel].altitude_raw),
                                     'az': np.rad2deg(event.mc.tel[id_tel].azimuth_raw)}

    def event_type(self, clean_level):
        if clean_level == "None":
            for tel_id in self.tel_ids:
                axes_camera = arrow_2d(self.event, tel_id, self.pointing)
                self.ren.AddActor(axes_camera)

                telescope = self.event.inst.subarray.tel[tel_id]

                tel_coords = self.event.inst.subarray.tel_coords
                tel_x_pos = tel_coords.x[tel_id - 1].value
                tel_y_pos = tel_coords.y[tel_id - 1].value
                tel_z_pos = tel_coords.z[tel_id - 1].value

                camera_actor = camera_structure(self.event, tel_id)
                camera_frame_actor = camera_frame(telescope.camera.cam_id)

                actorCollection = vtk.vtkActorCollection()

                actorCollection.AddItem(camera_actor)
                actorCollection.AddItem(camera_frame_actor)

                if telescope.optics.identifier[0] == "LST":
                    CSS_LST_actor = LST_tel_structure()
                    mirror_plate_actor = LST_create_mirror_plane()
                    actorCollection.AddItem(mirror_plate_actor)
                    actorCollection.AddItem(CSS_LST_actor)

                actorCollection.InitTraversal()

                for a in range(actorCollection.GetNumberOfItems()):
                    transform = vtk.vtkTransform()
                    transform.PostMultiply()
                    transform.RotateY(-self.pointing[tel_id]['alt'])
                    transform.Translate(tel_x_pos, tel_y_pos, tel_z_pos)
                    actor = actorCollection.GetNextActor()
                    actor.SetUserTransform(transform)
                    self.tel_id[tel_id].append(actor)

    def camera(self, elev=0):
        self.ren.GetActiveCamera().Elevation(elev-90)

    def show(self, width=920, height=640):
        for id_tel in self.tel_id:
            for actor in self.tel_id[id_tel]:
                self.ren.AddActor(actor)

        renwin = vtk.vtkRenderWindow()
        renwin.AddRenderer(self.ren)
        renwin.SetSize(width, height)
        iren = vtk.vtkRenderWindowInteractor()
        iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        iren.SetRenderWindow(renwin)

        self.ren.ResetCamera()

        renwin.Render()
        iren.Initialize()
        renwin.Render()
        iren.Start()
"""
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

pic_th = tail_cut[camera.cam_id][0]
bound_th = tail_cut[camera.cam_id][1]
image_cal = event.dl1.tel[tel_id].image[0]

mask_tail = tailcuts_clean(camera, image_cal,
                           picture_thresh=pic_th,
                           boundary_thresh=bound_th,
                           min_number_picture_neighbors=2)

cleaned = image_cal
cleaned[~mask_tail] = 0

fig = plt.figure(figsize=(6, 6))
plt.scatter(x_px, y_px, c=cleaned)
plt.show()

tableSize = image_cal.shape[0]

lut = MakeLUTFromCTF(cleaned)

render = CREED_VTK(event)
render.event_type("None")
render.camera(elev=20)
render.show()
"""