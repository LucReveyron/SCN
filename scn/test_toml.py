import ipcamera
from ipcamera import generate_ip_camera_from_toml


file_path = "/Users/lucreveyron/Documents/SCN/scn/config/camera_config.toml"

list_cam = generate_ip_camera_from_toml(file_path)

for camera in list_cam:
    print(camera.return_user())
