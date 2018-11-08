import vtk
import numpy as np
# Create points and cells for the spiral

nV = 256
nCyc = 10
rT1 = 0.2
rT2 = 0.5
rS = 4
h = 10
nTv = 8

points = vtk.vtkPoints()
for i in range(0, nV):
    # Spiral coordinates
    vX = rS * np.cos(2 * np.pi * nCyc * i / (nV - 1))
    vY = rS * np.sin(2 * np.pi * nCyc * i / (nV - 1))
    #vX = 10*np.cos(np.deg2rad(5*i))
    vZ = h * i / nV
    points.InsertPoint(i, vX, vY, vZ)

lines =  vtk.vtkCellArray()
lines.InsertNextCell(nV)

for i in range(0, nV):
    lines.InsertCellPoint(i)


polyData = vtk.vtkPolyData()
polyData.SetPoints(points)
polyData.SetLines(lines)

# Varying

tubeRadius =  vtk.vtkDoubleArray()
tubeRadius.SetName("TubeRadius")
tubeRadius.SetNumberOfTuples(nV)

for i in range(0, nV):
    tubeRadius.SetTuple1(i,rT1 + (rT2 - rT1) * np.sin(np.pi * i / (nV - 1)))

polyData.GetPointData().AddArray(tubeRadius)
polyData.GetPointData().SetActiveScalars("TubeRadius")

# RBG array(could add Alpha channel too I guess...)
# Varying from blue to red
colors = vtk.vtkUnsignedCharArray()
colors.SetName("Colors")
colors.SetNumberOfComponents(3)
colors.SetNumberOfTuples(nV)

for i in range(0, nV):
    colors.InsertTuple3(i,
                        int(255 * i / (nV - 1)),
                        0,
                        int(255 * (nV - 1 - i) / (nV - 1)))

polyData.GetPointData().AddArray(colors)

tube = vtk.vtkTubeFilter()
tube.SetInputData(polyData)

tube.SetNumberOfSides(nTv)
tube.SetVaryRadiusToVaryRadiusByAbsoluteScalar()

mapper =  vtk.vtkPolyDataMapper()
mapper.SetInputConnection(tube.GetOutputPort())
mapper.ScalarVisibilityOn()
mapper.SetScalarModeToUsePointFieldData()
mapper.SelectColorArray("Colors")

actor = vtk.vtkActor()
actor.SetMapper(mapper)

renderer = vtk.vtkRenderer()
renderer.AddActor(actor)
renderer.SetBackground(.2, .3, .4)

renderer.GetActiveCamera().Azimuth(30)
renderer.GetActiveCamera().Elevation(30)
renderer.ResetCamera()

renWin = vtk.vtkRenderWindow()
iren = vtk.vtkRenderWindowInteractor()

iren.SetRenderWindow(renWin)
renWin.AddRenderer(renderer)
renWin.SetSize(500, 500)
renWin.Render()

style = vtk.vtkInteractorStyleTrackballCamera()
iren.SetInteractorStyle(style)

iren.Start()