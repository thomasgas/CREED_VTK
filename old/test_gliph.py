import vtk

points = vtk.vtkPoints()
points.InsertNextPoint(0.0, 0.0, 0.0)
points.InsertNextPoint(5.0, 0.0, 0.0)
points.InsertNextPoint(10.0, 0.0, 0.0)

Colors = vtk.vtkUnsignedCharArray()
Colors.SetNumberOfComponents(3)
Colors.SetName("Colors")
Colors.InsertNextTuple3(255, 0, 0)
Colors.InsertNextTuple3(0, 255, 0)
Colors.InsertNextTuple3(0, 0, 255)

polydata = vtk.vtkPolyData()
polydata.SetPoints(points)
polydata.GetCellData().SetScalars(Colors)

cubeSource = vtk.vtkCubeSource()

glyph3D = vtk.vtkGlyph3D()

glyph3D.SetColorModeToColorByScalar()
glyph3D.SetSourceConnection(cubeSource.GetOutputPort())
glyph3D.SetInputData(polydata)
glyph3D.ScalingOff()
glyph3D.Update()

mapper = vtk.vtkPolyDataMapper()
mapper.SetInputData(glyph3D.GetOutPutPort())

actor = vtk.vtkActor()
actor.SetMapper(mapper)


# Create a renderer, render window, and interactor
WIDTH = 640
HEIGHT = 480
renderer = vtk.vtkRenderer()
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)
renderWindow.SetSize(WIDTH, HEIGHT)


# Add the actors to the scene
renderer.AddActor(actor)
renderer.SetBackground(0.7, 0.7, 0.7)  # Background color dark red

# Render and interact
renderWindowInteractor.Initialize()
renderWindow.Render()
renderWindowInteractor.Start()
