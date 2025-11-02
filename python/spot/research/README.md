### Deploying Policies:
https://docs.isaacsim.omniverse.nvidia.com/5.1.0/isaac_lab_tutorials/tutorial_policy_deployment.html 

My spot urdf order:
fl_hip
fl_uleg
fl_lleg
fr_hip
fr_uleg
fr_lleg
hl_hip
hl_uleg
hl_lleg
hr_hip
hr_uleg
hr_lleg

Robot Policy Breakdown:
Joint order:
['fl_hx', 'fr_hx', 'hl_hx', 'hr_hx', 'fl_hy', 'fr_hy', 'hl_hy', 'hr_hy', 'fl_kn', 'fr_kn', 'hl_kn', 'hr_kn']

Observations (48):
3 base_lin_vel
3 base_ang_vel
3 gravity
3 command
12 joint offset (current_joint_pos - default_pos)
12 joint velocities
12 previous action (the raw policy output)

Actions (12):
default_pos + (action * action_scale)

default_pos:
[0.1, -0.1, 0.1, -0.1, 0.9, 0.9, 1.1, 1.1, -1.5, -1.5, -1.5, -1.5]


My Robot:
{ 'body-Linear3Subhinge0': [array([0., 0., 0.]), array([0., 0., 0.]), array([0., 0., 0.]), array([0., 0., 0.])],
  'body-SphericalSubhinge1': [array([0., 0., 0.]), array([0., 0., 0.]), array([0., 0., 0.]), array([0., 0., 0.])],
  'body_inertia-LockedSubhinge0': [ array([], dtype=float64),
                                    array([], dtype=float64),
                                    array([], dtype=float64),
                                    array([], dtype=float64)],
  'fl_hip-PinSubhinge0': [array([0.]), array([0.]), array([0.]), array([0.])],
  'fl_lleg-PinSubhinge0': [array([0.]), array([0.]), array([0.]), array([0.])],
  'fl_uleg-PinSubhinge0': [array([0.]), array([0.]), array([0.]), array([0.])],
  'fr_hip-PinSubhinge0': [array([0.]), array([0.]), array([0.]), array([0.])],
  'fr_lleg-PinSubhinge0': [array([0.]), array([0.]), array([0.]), array([0.])],
  'fr_uleg-PinSubhinge0': [array([0.]), array([0.]), array([0.]), array([0.])],
  'hl_hip-PinSubhinge0': [array([0.]), array([0.]), array([0.]), array([0.])],
  'hl_lleg-PinSubhinge0': [array([0.]), array([0.]), array([0.]), array([0.])],
  'hl_uleg-PinSubhinge0': [array([0.]), array([0.]), array([0.]), array([0.])],
  'hr_hip-PinSubhinge0': [array([0.]), array([0.]), array([0.]), array([0.])],
  'hr_lleg-PinSubhinge0': [array([0.]), array([0.]), array([0.]), array([0.])],
  'hr_uleg-PinSubhinge0': [array([0.]), array([0.]), array([0.]), array([0.])]}

Conversions:
fl_hip  -> fl_hx
fr_hip  -> fr_hx
hl_hip  -> hl_hx
hr_hip  -> hr_hx
fl_uleg -> fl_hy
fr_uleg -> fr_hy
hl_uleg -> hl_hy
hr_uleg -> hr_hy
fl_lleg -> fl_kn
fr_lleg -> fr_kn
hl_lleg -> hl_kn
hr_lleg -> hr_kn