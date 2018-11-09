CREED_VTK
---------
This library relies on top of [ctapipe](https://github.com/cta-observatory/ctapipe) and it is intended to create 3D renderings 
in [VTK](https://www.vtk.org) for [CTA](www.cta-observatory.org) (the Cherenkov Telescope Array).

This library uses ctapipe to perform the analysis (import simtel file, extract telescopes positions, calibration, tailcut cleaning, etc...), so the standalone usage is not yet forecast. 

There is another similar package in my github repository called CREED, which uses OpenSCAD and SolidPython for the rendering: whether this is "easier" to be used, it is quite slow and not really nice to see (even though somehow it works). In order to create a more good looking, reliable and faster rendering library, I decided to use [VTK](https://www.vtk.org) (The Visualization Toolkit) which offers really better results (with a bit more of coding behind).

In a "ctapipe pipeline" one can introduce this library in this way (more or less...expect changes):

    from CREED_VTK import CREED_VTK

    render = CREED_VTK(event, telescopes_ids=[4,5,...])

    render.event_type(clean_level = "dl1", clean_dict=cleaned_dict)
    render.camera(elev=20)
    render.show(width= 1000, height=800)

    # TO BE IMPLEMENTED
    # render.ref_frames.tilted = TiltedFrame(...)
    # render.ref_frames.ground = GroundFrame(...)
    # render.ref_frame.tilted.arrows()
    # render.ref_frame.ground.arrows()
    # render.ref_frame.ground.grid()
    # render.ref_frame.ground.grid()
    # render.ref_frame.ground.add_point( x = 3 * u.m, 
                                       y = 5 * u.m,
                                       label = "mc"
                                      )
Where:

- `telescopes_ids` is optional: if not provided is taken from event.r0.tels_with_data
- `clean_level` can be: "r0", "dl1", "clean" (need to pass a dictionary with a `cleaned_image` as value and `telelscope_id` as key) or "None"

This will pop-out an OpenGL window with the camera, telescopes, etc... 
