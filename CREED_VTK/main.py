import copy
import vtk
import numpy as np
# from ctapipe.io import event_source
# from ctapipe.calib import CameraCalibrator
# from ctapipe.image import tailcuts_clean

from .camera.camera import *
from .utils.arrows import *
from .telescope.LST import *
from .telescope.MST import *
from .telescope.SST import *
from .utils.cam_utils import *
from .frames import *

from ctapipe.coordinates import HorizonFrame

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
        self.ren.SetBackground(0.9, 0.9, 0.9)
        self.array_pointing = HorizonFrame(alt=np.rad2deg(event.mcheader.run_array_direction[1]),
                                           az=np.rad2deg(event.mcheader.run_array_direction[0]))
        self.pointing = {}

        for tel_id in self.tel_ids:
            self.tel_id[tel_id] = []
            self.pointing[tel_id] = {'alt': np.rad2deg(event.mc.tel[tel_id].altitude_raw),
                                     'az': np.rad2deg(event.mc.tel[tel_id].azimuth_raw)}

    def add_arrows_camera_frame(self):
        for tel_id in self.tel_ids:

            telescope = self.event.inst.subarray.tel[tel_id]
            camera_type = telescope.camera.cam_id

            tel_coords = self.event.inst.subarray.tel_coords
            tel_x_pos = tel_coords.x[tel_id - 1].value
            tel_y_pos = tel_coords.y[tel_id - 1].value
            tel_z_pos = tel_coords.z[tel_id - 1].value

            axes_camera = arrow_2d(arrow_length=10, x_label="x_sim", y_label="y_sim")

            transform_arrow = vtk.vtkTransform()
            transform_arrow.Translate(tel_x_pos, tel_y_pos, tel_z_pos)
            transform_arrow.RotateY(-self.pointing[tel_id]['alt'])
            transform_arrow.Translate(get_cam_height(camera_type), 0.0, 0.0)
            transform_arrow.RotateY(90)

            axes_camera.SetUserTransform(transform_arrow)

            self.ren.AddActor(axes_camera)

    def event_type(self, clean_level, clean_dict=None):
        for tel_id in self.tel_ids:

            telescope = self.event.inst.subarray.tel[tel_id]

            # tel_coords = self.event.inst.subarray.tel_coords
            tel_x_pos = self.tel_coords.x[tel_id - 1].value
            tel_y_pos = self.tel_coords.y[tel_id - 1].value
            tel_z_pos = self.tel_coords.z[tel_id - 1].value
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

    def camera_view(self, elev=0):
        self.ren.GetActiveCamera().Elevation(elev-90)

    def tel_labels(self):
        for id_tel in self.tel_id:
            tel_x_pos = self.tel_coords.x[id_tel - 1].value
            tel_y_pos = self.tel_coords.y[id_tel - 1].value
            tel_z_pos = self.tel_coords.z[id_tel - 1].value
            tel_label = create_extruded_text(text=str(id_tel))
            tel_label = scale_object(tel_label, 8)
            tel_label = translate_object(tel_label, center=[tel_x_pos + 8,
                                                            tel_y_pos + 8,
                                                            tel_z_pos])

            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(tel_label.GetOutputPort())

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            self.ren.AddActor(actor)

    def add_gnd_tels(self):
        self.ren.AddActor(create_ground_positions(self.event, self.tel_ids))

    def add_gnd_frame(self, size):
        self.ren.AddActor(create_ground_frame(size))

    def add_tilted_tels(self):
        self.ren.AddActor(add_tilted_positions(self.tel_coords,
                                               self.tel_ids,
                                               array_pointing=self.array_pointing))

    def add_tilted_frame(self, size):
        self.ren.AddActor(create_tilted_frame(array_pointing=self.array_pointing, size=size))

    def show(self, width=920, height=640):
        """
        Display the rendering. window size is 920 x 640 is the default
        :param width: in pixels
        :param height: in pixels
        :return:
        """
        for id_tel in self.tel_id:
            for actor in self.tel_id[id_tel]:
                self.ren.AddActor(actor)

        axes_gnd = arrow_3d(arrow_length=30,
                            x_label="x_gnd=North",
                            y_label="y_gnd=West",
                            z_label="z_gnd=Zen")

        self.ren.AddActor(axes_gnd)

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