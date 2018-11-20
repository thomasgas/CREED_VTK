import copy
import vtk
import numpy as np
# from ctapipe.io import event_source
# from ctapipe.calib import CameraCalibrator
# from ctapipe.image import tailcuts_clean

from .camera.camera import camera_frame, camera_structure
from .utils.arrows import arrow_2d
from .telescope.LST import LST_create_mirror_plane, LST_tel_structure
from .telescope.MST import MST_create_mirror_plane, MST_tel_structure
from .telescope.SST import SST_tel_structure, SST_primary_mirror_plane
from .utils.cam_utils import get_cam_height

tail_cut = {"LSTCam": (10, 20),
            "NectarCam": (7, 14),
            "FlashCam": (7, 14),
            "SCTCam": (5, 10),
            "CHEC": (3, 6),
            "DigiCam": (3, 6),
            "ASTRICam": (5, 10)}


class CREED_VTK:
    def __init__(self, event, telescopes_ids=None):
        self.event = event
        if telescopes_ids is None:
            self.tel_ids = list(event.r0.tels_with_data)
        else:
            self.tel_ids = telescopes_ids

        self.tel_id = {}
        self.tel_coords = event.inst.subarray.tel_coords
        self.ren = vtk.vtkRenderer()
        self.ren.SetBackground(0.8, 0.8, 0.8)
        self.pointing = {}

        for id_tel in self.tel_ids:
            self.tel_id[id_tel] = []
            self.pointing[id_tel] = {'alt': np.rad2deg(event.mc.tel[id_tel].altitude_raw),
                                     'az': np.rad2deg(event.mc.tel[id_tel].azimuth_raw)}

    def event_type(self, clean_level, clean_dict=None):
        for tel_id in self.tel_ids:

            telescope = self.event.inst.subarray.tel[tel_id]

            tel_coords = self.event.inst.subarray.tel_coords
            tel_x_pos = tel_coords.x[tel_id - 1].value
            tel_y_pos = tel_coords.y[tel_id - 1].value
            tel_z_pos = tel_coords.z[tel_id - 1].value

            axes_camera = arrow_2d(self.event, tel_id, self.pointing)
            # axes_camera.SetPosition(tel_x_pos,
            #                         tel_y_pos,
            #                         tel_z_pos + get_cam_height(telescope.camera.cam_id))
            self.ren.AddActor(axes_camera)

            camera_actor = camera_structure(self.event, tel_id, clean_level, clean_dict)
            camera_frame_actor = camera_frame(telescope.camera.cam_id)

            actorCollection = vtk.vtkActorCollection()

            actorCollection.AddItem(camera_actor)
            actorCollection.AddItem(camera_frame_actor)

            if telescope.optics.identifier[0] == "LST":
                CSS_LST_actor = LST_tel_structure()
                mirror_plate_actor = LST_create_mirror_plane()
                actorCollection.AddItem(mirror_plate_actor)
                actorCollection.AddItem(CSS_LST_actor)
            elif telescope.optics.identifier[0] == "MST":
                MST_mirror_plate_actor = MST_create_mirror_plane()
                MST_tel_structure_actor = MST_tel_structure()
                actorCollection.AddItem(MST_mirror_plate_actor)
                actorCollection.AddItem(MST_tel_structure_actor)
            elif telescope.optics.identifier[0] == 'SST':
                SST_primary_mirror_plane_actor = SST_primary_mirror_plane()
                SST_tel_structure_actor = SST_tel_structure()
                actorCollection.AddItem(SST_primary_mirror_plane_actor)
                actorCollection.AddItem(SST_tel_structure_actor)


            actorCollection.InitTraversal()

            transform = vtk.vtkTransform()
            transform.PostMultiply()
            transform.RotateY(-self.pointing[tel_id]['alt'])
            transform.Translate(tel_x_pos, tel_y_pos, tel_z_pos)

            for a in range(actorCollection.GetNumberOfItems()):
                actor = actorCollection.GetNextActor()
                actor.SetUserTransform(transform)
                self.tel_id[tel_id].append(actor)

    def camera(self, elev=0):
        self.ren.GetActiveCamera().Elevation(elev-90)

    def show(self, width=920, height=640):
        for id_tel in self.tel_id:
            for actor in self.tel_id[id_tel]:
                self.ren.AddActor(actor)

        axes_gnd = vtk.vtkAxesActor()
        axes_gnd.SetTotalLength(10, 10, 10)
        axes_gnd.SetShaftTypeToCylinder()
        axes_gnd.GetXAxisCaptionActor2D().GetTextActor().SetTextScaleMode(3)
        axes_gnd.GetYAxisCaptionActor2D().GetTextActor().SetTextScaleMode(3)
        axes_gnd.GetZAxisCaptionActor2D().GetTextActor().SetTextScaleMode(3)
        # self.ren.AddActor(axes_gnd)

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