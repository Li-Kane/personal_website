import torch

policy = torch.jit.load("spot_policy.pt", map_location="cpu")
policy.eval()

import numpy as np

obs_neutral = np.array([
    # 0:3  base lin vel (body) [m/s]
     0.00,  0.00,  0.00,
    # 3:6  base ang vel (body) [rad/s]
     0.00,  0.00,  0.00,
    # 6:9  projected gravity in body frame (unit vector)
     0.00,  0.00, -1.00,
    # 9:12 commanded [v_x, v_y, w_z]
     0.50,  0.00,  0.20,
    # 12:24 joint pos offsets = (q_current - default_pos) [rad]
     0.00,  0.00,  0.00,  0.00,  0.00,  0.00,
     0.00,  0.00,  0.00,  0.00,  0.00,  0.00,
    # 24:36 joint vels [rad/s]
     0.00,  0.00,  0.00,  0.00,  0.00,  0.00,
     0.00,  0.00,  0.00,  0.00,  0.00,  0.00,
    # 36:48 previous action (last 12 joint pos targets in [-1,1] space)
     0.00,  0.00,  0.00,  0.00,  0.00,  0.00,
     0.00,  0.00,  0.00,  0.00,  0.00,  0.00,
], dtype=np.float32)

observation = obs_neutral

obs = torch.as_tensor(observation, dtype=torch.float32).view(1, -1)
with torch.no_grad():
    action = policy(obs)                 # -> (1, 12)
action = action.squeeze(0).cpu().numpy()
print("Action: ", action)
