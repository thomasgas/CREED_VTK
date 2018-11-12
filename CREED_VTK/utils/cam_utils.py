def get_cam_height(cam_type):

    if cam_type == "LSTCam":
        cam_height = 28
    elif cam_type == "FlashCam" or cam_type == "NectarCam":
        cam_height = 16
    elif cam_type == "CHEC" or cam_type == "DigiCam" or cam_type =="ASTRICam":
        cam_height = 4
    else:
        cam_height = 50
        print("wrong camera given")

    return cam_height
