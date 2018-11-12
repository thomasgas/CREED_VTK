import vtk
import numpy as np
from vtk.util.colors import tomato
from ..utils.cam_utils import get_cam_height

primary_reflector_diameter = 4.0
cam_height = get_cam_height("CHEC")


def SST_tel_structure():

    l = primary_reflector_diameter / (2 * (2 ** 0.5))

    x_points = [l, l, -l, -l]
    y_points = [-l, l, l, -l]
    appendFilter = vtk.vtkAppendPolyData()

    for i in range(4):
        input1 = vtk.vtkPolyData()

        # Create a cylinder.
        # Cylinder height vector is (0,1,0).
        # Cylinder center is in the middle of the cylinder
        cylinderSource = vtk.vtkCylinderSource()
        cylinderSource.SetResolution(15)
        cylinderSource.SetRadius(0.1)
        cylinderSource.Update()

        # Generate a random start and end point
        startPoint = [x_points[i], y_points[i], 0]
        endPoint = [x_points[i]/4, y_points[i]/4, cam_height]
        rng = vtk.vtkMinimalStandardRandomSequence()
        rng.SetSeed(8775070)  # For testing.

        normalizedX = [0, 0, 0]
        normalizedY = [0, 0, 0]
        normalizedZ = [0, 0, 0]

        # The X axis is a vector from start to end
        vtk.vtkMath.Subtract(endPoint, startPoint, normalizedX)
        length = vtk.vtkMath.Norm(normalizedX)
        vtk.vtkMath.Normalize(normalizedX)

        # The Z axis is an arbitrary vector cross X
        arbitrary = [0, 0, 0]
        for i in range(0, 3):
            rng.Next()
            arbitrary[i] = rng.GetRangeValue(-10, 10)
        vtk.vtkMath.Cross(normalizedX, arbitrary, normalizedZ)
        vtk.vtkMath.Normalize(normalizedZ)

        # The Y axis is Z cross X
        vtk.vtkMath.Cross(normalizedZ, normalizedX, normalizedY)
        matrix = vtk.vtkMatrix4x4()

        # Create the direction cosine matrix
        matrix.Identity()
        for i in range(0, 3):
            matrix.SetElement(i, 0, normalizedX[i])
            matrix.SetElement(i, 1, normalizedY[i])
            matrix.SetElement(i, 2, normalizedZ[i])

        # Apply the transforms
        transform = vtk.vtkTransform()
        transform.Translate(startPoint)  # translate to starting point
        transform.Concatenate(matrix)  # apply direction cosines
        transform.RotateZ(-90.0)  # align cylinder to x axis
        transform.Scale(1.0, length, 1.0)  # scale along the height vector
        transform.Translate(0, .5, 0)  # translate to start of cylinder
        transform.Update()

        # Transform the polydata
        transformPD = vtk.vtkTransformPolyDataFilter()
        transformPD.SetTransform(transform)
        transformPD.SetInputConnection(cylinderSource.GetOutputPort())
        transformPD.Update()

        input1.ShallowCopy(transformPD.GetOutput())

        appendFilter.AddInputData(input1)

    appendFilter.Update()

    cleanFilter = vtk.vtkCleanPolyData()
    cleanFilter.SetInputConnection(appendFilter.GetOutputPort())
    cleanFilter.Update()

    # Create a mapper and actor for the arrow
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(cleanFilter.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.RotateY(90)
    return actor


def SST_primary_mirror_plane():

    sphereSource1 = vtk.vtkSphereSource()
    sphereSource1.SetCenter(0.3, 0, 0)
    sphereSource1.SetRadius(cam_height)
    sphereSource1.SetThetaResolution(30)
    sphereSource1.SetPhiResolution(30)
    sphereSource1.Update()
    input1 = sphereSource1.GetOutput()
    sphere1Tri = vtk.vtkTriangleFilter()
    sphere1Tri.SetInputData(input1)

    sphereSource2 = vtk.vtkSphereSource()
    sphereSource2.SetRadius(cam_height)
    sphereSource2.SetThetaResolution(30)
    sphereSource2.SetPhiResolution(30)
    sphereSource2.Update()
    input2 = sphereSource2.GetOutput()
    sphere2Tri = vtk.vtkTriangleFilter()
    sphere2Tri.SetInputData(input2)

    booleanOperation = vtk.vtkBooleanOperationPolyDataFilter()
    # booleanOperation.SetOperationToUnion()
    # booleanOperation.SetOperationToIntersection()
    booleanOperation.SetOperationToDifference()

    booleanOperation.SetInputConnection(1, sphere1Tri.GetOutputPort())
    booleanOperation.SetInputConnection(0, sphere2Tri.GetOutputPort())
    booleanOperation.Update()

    bool_cylinder = vtk.vtkCylinderSource()
    bool_cylinder.SetCenter(0, 0, 0)
    bool_cylinder.SetRadius(primary_reflector_diameter/2)
    bool_cylinder.SetHeight(cam_height*2)
    bool_cylinder.SetResolution(40)
    # sphereSource3.SetResolution(20)
    bool_cylinder.Update()

    transform = vtk.vtkTransform()
    transform.Translate(-cam_height, 0, 0)
    transform.RotateZ(90)

    transformFilter = vtk.vtkTransformPolyDataFilter()
    transformFilter.SetTransform(transform)
    transformFilter.SetInputConnection(bool_cylinder.GetOutputPort())
    transformFilter.Update()

    input3 = transformFilter.GetOutput()
    cylinderTri = vtk.vtkTriangleFilter()
    cylinderTri.SetInputData(input3)

    booleanCylinderIntersect = vtk.vtkBooleanOperationPolyDataFilter()
    booleanCylinderIntersect.SetOperationToIntersection()
    # booleanCylinderIntersect.SetOperationToUnion()

    booleanCylinderIntersect.SetInputConnection(0, booleanOperation.GetOutputPort())
    booleanCylinderIntersect.SetInputConnection(1, cylinderTri.GetOutputPort())
    booleanCylinderIntersect.Update()

    booleanOperationMapper = vtk.vtkPolyDataMapper()
    booleanOperationMapper.SetInputConnection(booleanCylinderIntersect.GetOutputPort())
    booleanOperationMapper.ScalarVisibilityOff()

    booleanOperationActor = vtk.vtkActor()
    booleanOperationActor.SetMapper(booleanOperationMapper)
    booleanOperationActor.SetPosition(cam_height - 0.8, 0, 0)

    return booleanOperationActor
