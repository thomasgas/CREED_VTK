import vtk
import numpy as np

from .camera.camera import *
from .utils.arrows import *
from .telescope.LST import *
from .telescope.MST import *
from .telescope.SST import *
from .utils.cam_utils import *
from .frames import *

from astropy.coordinates import AltAz, SkyCoord, spherical_to_cartesian
import astropy.units as u

from sympy import Plane

from ctapipe.coordinates import TiltedGroundFrame, GroundFrame, project_to_ground

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

        # dictionary to save the actor per each telescope
        self.tel_id = {}
        self.tel_coords = {}  # event.inst.subarray.tel_coords

        self.subarray = self.event.inst.subarray

        for tel_id in self.tel_ids:
            coords = self.subarray.tel_coords[self.subarray.tel_indices[tel_id]]
            self.tel_coords[tel_id] = coords

        self.ren = vtk.vtkRenderer()
        self.ren.SetBackground(0.9, 0.9, 0.9)

        try:
            self.array_pointing = SkyCoord(
                alt=np.rad2deg(event.mcheader.run_array_direction[1]),
                az=np.rad2deg(event.mcheader.run_array_direction[0]),
                frame=AltAz()
            )
        except ValueError:
            self.array_pointing = SkyCoord(
                alt=event.mc.alt,
                az=event.mc.az,
                frame=AltAz()
            )
        self.tilted_frame = TiltedGroundFrame(pointing_direction=self.array_pointing)

        self.pointing = {}

        for tel_id in self.tel_ids:
            self.tel_id[tel_id] = []
            self.pointing[tel_id] = {'alt': np.rad2deg(event.mc.tel[tel_id].altitude_raw),
                                     'az': np.rad2deg(event.mc.tel[tel_id].azimuth_raw)}

    def add_arrows_camera_frame(self):
        for tel_id in self.tel_ids:
            tel_x_pos = self.tel_coords[tel_id].x.to_value(u.m)
            tel_y_pos = self.tel_coords[tel_id].y.to_value(u.m)
            tel_z_pos = self.tel_coords[tel_id].z.to_value(u.m)

            telescope = self.event.inst.subarray.tel[tel_id]
            camera_type = telescope.camera.cam_id

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
            tel_x_pos = self.tel_coords[tel_id].x.to_value(u.m)
            tel_y_pos = self.tel_coords[tel_id].y.to_value(u.m)
            tel_z_pos = self.tel_coords[tel_id].z.to_value(u.m)

            camera_actor = camera_structure(self.event, tel_id, clean_level, clean_dict)
            camera_frame_actor = camera_frame(telescope.camera.cam_id)

            actorCollection = vtk.vtkActorCollection()

            actorCollection.AddItem(camera_actor)
            actorCollection.AddItem(camera_frame_actor)

            if telescope.optics.name == "LST":
                CSS_LST_actor = LST_tel_structure()
                mirror_plate_actor = LST_create_mirror_plane()
                actorCollection.AddItem(mirror_plate_actor)
                actorCollection.AddItem(CSS_LST_actor)
            elif telescope.optics.name == "MST":
                MST_mirror_plate_actor = MST_create_mirror_plane()
                MST_tel_structure_actor = MST_tel_structure()
                actorCollection.AddItem(MST_mirror_plate_actor)
                actorCollection.AddItem(MST_tel_structure_actor)
            elif telescope.optics.name == 'SST':
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

    def tel_labels(self, frame="ground", tilted_pos=None):
        """
        Frame can be either "ground" or "tilted"
        :param frame:
        :param tilted_pos: coordinates in the TiltedGroundFrame
        :return:
        """
        for id_tel in self.tel_ids:
            if frame == "ground":
                tel_x_pos = self.tel_coords[id_tel].x.to_value(u.m)
                tel_y_pos = self.tel_coords[id_tel].y.to_value(u.m)
                tel_z_pos = self.tel_coords[id_tel].z.to_value(u.m)
            elif frame == "tilted":
                tel_x_pos = tilted_pos[id_tel][0]
                tel_y_pos = tilted_pos[id_tel][1]
                tel_z_pos = tilted_pos[id_tel][2]

            tel_label = create_extruded_text(text=str(id_tel))
            tel_label = scale_object(tel_label, 8)
            tel_label = translate_object(tel_label,
                                         center=[tel_x_pos + 5,
                                                 tel_y_pos + 5,
                                                 tel_z_pos + 10])

            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(tel_label.GetOutputPort())

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            if frame == "tilted":
                actor.RotateZ(- self.array_pointing.az.value)
                actor.RotateY(90 - self.array_pointing.alt.value)

            self.ren.AddActor(actor)

    def add_gnd_tels(self):
        self.ren.AddActor(create_ground_positions(self.tel_coords, self.tel_ids))

    def add_gnd_frame(self, size):
        self.ren.AddActor(create_ground_frame(size))

    def add_tilted_tels(self, tel_labels=False):
        tilted_positions = {}
        tel_coords_gnd = self.subarray.tel_coords

        tilted_system = TiltedGroundFrame(pointing_direction=self.array_pointing)
        tilt_tel_pos = tel_coords_gnd.transform_to(tilted_system)

        for tel_id in self.tel_ids:
            tel_x_pos = tilt_tel_pos[self.subarray.tel_indices[tel_id]].x.to_value(u.m)
            tel_y_pos = tilt_tel_pos[self.subarray.tel_indices[tel_id]].y.to_value(u.m)
            tel_z_pos = 0
            tilted_positions[tel_id] = [tel_x_pos, tel_y_pos, tel_z_pos]

        if tel_labels is True:
            self.tel_labels(frame="tilted", tilted_pos=tilted_positions)

        self.ren.AddActor(
            add_tilted_positions(
                tilted_positions,
                array_pointing=self.array_pointing
            )
        )

    def add_tilted_frame(self, size):
        self.ren.AddActor(
            create_tilted_frame(
                array_pointing=self.array_pointing,
                size=size
            )
        )

    def add_impact_point(self, label=None, status="mc", frame="ground", gnd_reco_pos=None):

        if label is None:
            label = ""
        if frame == "ground":
            if status == "mc":
                core_x_pos = self.event.mc.core_x.to_value(u.m)
                core_y_pos = self.event.mc.core_y.to_value(u.m)
                core_z_pos = 0
            elif status == "reco":
                core_x_pos = gnd_reco_pos.x.to_value(u.m)
                core_y_pos = gnd_reco_pos.y.to_value(u.m)
                core_z_pos = 0

        elif frame == "tilted":
            tilted_frame = TiltedGroundFrame(pointing_direction=self.array_pointing)

            if status == "mc":
                gnd_core_mc = GroundFrame(x=self.event.mc.core_x,
                                          y=self.event.mc.core_y,
                                          z=0.0 * u.m)
                tilted_core_mc = gnd_core_mc.transform_to(tilted_frame)
            elif status == "reco":
                tilted_core_mc = gnd_reco_pos.transform_to(tilted_frame)

            core_x_pos = tilted_core_mc.x.to_value(u.m)
            core_y_pos = tilted_core_mc.y.to_value(u.m)
            core_z_pos = 0

        tel_label = create_extruded_text(text=label)
        tel_label = scale_object(tel_label, 20)
        # those "magic numbers" are needed to have the center of the first letter
        # of the label in the exact position. Depends on the fontsize.
        tel_label = translate_object(
            tel_label,
            center=[core_x_pos - 12,
                    core_y_pos - 9,
                    core_z_pos]
        )

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(tel_label.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor([0, 0, 255])
        if frame == "tilted":
            actor.RotateZ(- self.array_pointing.az.value)
            actor.RotateY(90 - self.array_pointing.alt.value)
        self.ren.AddActor(actor)

    def plot_hillas_lines(self, hillas_dict, length, frame="ground"):

        # xx, yy, zz = np.array(spherical_to_cartesian(
        #     1,
        #     self.array_pointing.alt,
        #     0 * u.deg)
        # )  # -self.array_pointing.az))
        # # plane = Plane(Point3D(0, 0, 0), normal_vector=(xx, yy, zz))

        tilted_system = self.tilted_frame
        tel_coords_gnd = self.subarray.tel_coords
        tilt_tel_pos = tel_coords_gnd.transform_to(tilted_system)

        for tel_id in self.tel_ids:
            moments = hillas_dict[tel_id]
            if frame == "ground":
                color = [255, 0, 0]
                gnd_pos = project_to_ground(tilt_tel_pos[self.subarray.tel_indices[tel_id]])
                tel_x_pos = gnd_pos.x.to_value(u.m)
                tel_y_pos = gnd_pos.y.to_value(u.m)
                tel_z_pos = gnd_pos.z.to_value(u.m)

            elif frame == "tilted":
                color = [0, 255, 0]
                # i need those coordinates in GroundFrame to transform to TiltedGroundFrame
                # The selection is done afterwards
                tel_x_pos = tilt_tel_pos[self.subarray.tel_indices[tel_id]].x.to_value(u.m)
                tel_y_pos = tilt_tel_pos[self.subarray.tel_indices[tel_id]].y.to_value(u.m)
                tel_z_pos = 0
                # tilted_tel_pos = tilt_tel_pos[self.subarray.tel_indices[tel_id]]

            hillas_line_actor = hillas_lines(
                moments=moments,
                length=length,
                tel_coords=[tel_x_pos, tel_y_pos, tel_z_pos],
                frame=frame,
                array_pointing=self.array_pointing,
                tilted_frame=tilted_system,
                # plane=plane,

            )

            # if frame == "tilted":
            #     hillas_line_actor.RotateZ(0)#self.array_pointing.az.value)
            #     hillas_line_actor.RotateY(0)#90 - self.array_pointing.alt.value)

            # self.tel_id[tel_id].append(hillas_line_actor)
            hillas_line_actor.GetProperty().SetColor(color)
            self.ren.AddActor(hillas_line_actor)

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

        axes_gnd = arrow_3d(arrow_length=50,
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
