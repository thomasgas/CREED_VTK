def get_cam_height(cam_type):
    if cam_type == "LSTCam":
        cam_height = 28
    elif cam_type == "FlashCam" or "NectarCam":
        cam_height = 16
    else:
        cam_height = 50
        print("wrong camera given")
    return cam_height
