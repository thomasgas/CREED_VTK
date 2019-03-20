from .transf_utils import *
import astropy.units as u
import numpy as np
# from sympy import Point3D, Ray3D
import astropy.units as u

from ctapipe.coordinates import project_to_ground
from astropy.coordinates import SkyCoord
from ctapipe.utils.linalg import angle as angle_util


def arrow_2d(arrow_length=10, x_label="x", y_label="y"):
    """
    Create 2d arrows with labels
    :param arrow_length: specify arrow length
    :param x_label: Label for x axis
    :param y_label: label for y axis
    :return: return actor with arrows and labels. Can be transformed as an actor then.
    """
    mbds = vtk.vtkMultiBlockDataSet()

    arrows = 2

    # allocate space for arrows and text
    mbds.SetNumberOfBlocks(2 * arrows + 1)

    # Leave block 1 NULL.  NULL blocks are valid and should be handled by
    # algorithms that process multiblock datasets.  Especially when
    # running in parallel where the blocks owned by other processes are
    # NULL in this process.

    single_arrow = scale_object(create_arrow(), length=arrow_length)

    X_arrow = single_arrow
    Y_arrow = rotate_object(single_arrow, "z", 90)

    x_text = translate_object(create_extruded_text(x_label), [arrow_length, 0, 0])

    y_text = rotate_object(create_extruded_text(y_label), "z", 90)
    y_text = translate_object(y_text, [0, arrow_length, 0])

    mbds.SetBlock(0, X_arrow.GetOutput())
    mbds.SetBlock(2, Y_arrow.GetOutput())
    mbds.SetBlock(3, x_text.GetOutput())
    mbds.SetBlock(4, y_text.GetOutput())

    mapper = vtk.vtkCompositePolyDataMapper2()
    mapper.SetInputDataObject(mbds)

    cdsa = vtk.vtkCompositeDataDisplayAttributes()
    mapper.SetCompositeDataDisplayAttributes(cdsa)

    red = (255, 0, 0)
    green = (0, 255, 0)

    mapper.SetBlockColor(1, red)
    mapper.SetBlockColor(3, green)
    mapper.SetBlockColor(4, red)
    mapper.SetBlockColor(5, green)

    axes = vtk.vtkActor()
    axes.SetMapper(mapper)

    return axes


def arrow_3d(arrow_length=10, x_label="x", y_label="y", z_label="z"):
    """
    Create 3d arrow with labels
    :param arrow_length: specify arrow length
    :param x_label: label for x axis
    :param y_label: label for y axis
    :param z_label: label for z axis
    :return: return 3d arrow as an actor. Can be transformed in the main.py
    """
    # tel_coords = event.inst.subarray.tel_coords
    #
    # telescope = event.inst.subarray.tel[tel_id]
    # camera_type = telescope.camera.cam_id
    #
    # tel_x_pos = tel_coords.x[tel_id - 1].value
    # tel_y_pos = tel_coords.y[tel_id - 1].value
    # tel_z_pos = tel_coords.z[tel_id - 1].value
    #
    # transform_arrow = vtk.vtkTransform()
    # transform_arrow.Translate(tel_x_pos, tel_y_pos, tel_z_pos)
    # transform_arrow.RotateY(-pointing[tel_id]['alt'])
    # transform_arrow.Translate(get_cam_height(camera_type), 0.0, 0.0)
    # transform_arrow.RotateY(90)

    mbds = vtk.vtkMultiBlockDataSet()

    arrows = 3

    # allocate space for arrows and text
    mbds.SetNumberOfBlocks(2 * arrows + 1)

    # Leave block 1 NULL.  NULL blocks are valid and should be handled by
    # algorithms that process multiblock datasets.  Especially when
    # running in parallel where the blocks owned by other processes are
    # NULL in this process.

    single_arrow = scale_object(create_arrow(), length=arrow_length)

    X_arrow = single_arrow
    Y_arrow = rotate_object(single_arrow, "z", 90)
    Z_arrow = rotate_object(single_arrow, "y", -90)

    x_text = scale_object(create_extruded_text(x_label), length=arrow_length/10)
    x_text = translate_object(x_text, [arrow_length, 0, 0])

    y_text = scale_object(create_extruded_text(y_label), length=arrow_length/10)
    y_text = rotate_object(y_text, "z", 90)
    y_text = translate_object(y_text, [0, arrow_length, 0])

    z_text = scale_object(create_extruded_text(z_label), length=arrow_length/10)
    z_text = rotate_object(z_text, "y", -90)
    z_text = translate_object(z_text, [0, 0, arrow_length])

    mbds.SetBlock(0, X_arrow.GetOutput())
    mbds.SetBlock(2, Y_arrow.GetOutput())
    mbds.SetBlock(3, Z_arrow.GetOutput())
    mbds.SetBlock(4, x_text.GetOutput())
    mbds.SetBlock(5, y_text.GetOutput())
    mbds.SetBlock(6, z_text.GetOutput())

    mapper = vtk.vtkCompositePolyDataMapper2()
    mapper.SetInputDataObject(mbds)

    cdsa = vtk.vtkCompositeDataDisplayAttributes()
    mapper.SetCompositeDataDisplayAttributes(cdsa)

    # You can use the vtkCompositeDataDisplayAttributes to set the color,
    # opacity and visibiliy of individual blocks of the multiblock dataset.
    # Attributes are mapped by block pointers (vtkDataObject*), so these can
    # be queried by their flat index through a convenience function in the
    # attribute class (vtkCompositeDataDisplayAttributes::DataObjectFromIndex).
    # Alternatively, one can set attributes directly through the mapper using
    # flat indices.
    #
    # This sets the block at flat index 3 red
    # Note that the index is the flat index in the tree, so the whole multiblock
    # is index 0 and the blocks are flat indexes 1, 2 and 3.  This affects
    # the block returned by mbds.GetBlock(2).
    # double color[] = {1, 0, 0}

    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)

    mapper.SetBlockColor(1, red)
    mapper.SetBlockColor(3, green)
    mapper.SetBlockColor(4, blue)
    mapper.SetBlockColor(5, red)
    mapper.SetBlockColor(6, green)
    mapper.SetBlockColor(7, blue)

    axes = vtk.vtkActor()
    axes.SetMapper(mapper)
    # axes.SetUserTransform(transform_arrow)

    return axes


def hillas_lines(moments, length, tel_coords, frame, array_pointing, tilted_frame, plane=None):

    angle_in = moments.psi.to_value(u.rad)

    # a = Point3D(1, 0, 0)
    # b = Point3D(np.cos(angle), np.sin(angle), 0)

    if frame == "tilted":
        angle = angle_in + np.pi/2.

        # origin = Point3D(0, 0, 0)
        # line_a = Ray3D(origin, a)
        # line_b = Ray3D(origin, b)
        # angle_tilt = line_b.angle_between(line_a)
        # angle_tilted = (float(angle_tilt.evalf()) * u.rad).to_value(u.deg)

        a = np.array([1, 0, 0])
        b = np.array([np.cos(angle), np.sin(angle), 0])
        angle_tilt_np = u.Quantity(angle_util(a, b), u.rad).to_value(u.deg)
        psi = angle_tilt_np
    elif frame == "ground":
        # b_in_plane = plane.projection(b)
        # a_in_plane = plane.projection(a)
        # line_a_plane = Ray3D(origin, a_in_plane)
        # line_b_plane = Ray3D(origin, b_in_plane)
        # angle_gnd = line_b_plane.angle_between(line_a_plane)
        # angle_ground = (float(angle_gnd.evalf()) * u.rad).to_value(u.deg)
        # psi = angle_ground - array_pointing.az.to_value(u.deg)

        if angle_in < 0:
            angle_in = angle_in + np.pi

        angle = angle_in

        fix_a_in_plane = SkyCoord(x=1 * u.m, y=0 * u.m, frame=tilted_frame)
        fix_b_in_plane = SkyCoord(x=np.cos(angle) * u.m, y=np.sin(angle) * u.m, frame=tilted_frame)

        angle_fix_np = u.Quantity(
            angle_util(
                project_to_ground(fix_a_in_plane).cartesian.xyz.to_value(u.m),
                project_to_ground(fix_b_in_plane).cartesian.xyz.to_value(u.m)),
            u.rad
        ).to_value(u.deg)

        psi = angle_fix_np - array_pointing.az.to_value(u.deg) + 90

    cylinder = vtk.vtkCylinderSource()
    cylinder.SetResolution(4)
    cylinder.SetRadius(1)
    cylinder.SetHeight(length)
    cylinder.Update()

    rotate_cylinder = rotate_object(cylinder, 'z', psi)

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(rotate_cylinder.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    transform = vtk.vtkTransform()
    transform.PostMultiply()
    transform.Translate(*tel_coords)

    if frame == "tilted":
        transform.RotateY(90 - array_pointing.alt.value)
        transform.RotateZ(- array_pointing.az.value)

    actor.SetUserTransform(transform)

    return actor

