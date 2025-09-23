import kdwidgets
from env import ATRVEnv
import gymnasium as gym
from stable_baselines3 import SAC
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
import numpy as np

gym.register(
    id="kdFlex-ATRVjr",
    entry_point=ATRVEnv,
)

def main():
    # setup simulation
    env = gym.make("kdFlex-ATRVjr", port=3247, render_mode="human", sync_real_time=True)
    env = DummyVecEnv([lambda: env])
    env = VecNormalize.load("./models/demo_vec_normalize.pkl", env)
    env.training = False
    env.norm_reward = False
    model = SAC.load("./models/demo_model", env=env)

    # setup widgets
    iframe_layout = {
        "height": "100%",
        "width": "100%",
        "overflow": "hidden",
    }
    iframe_style = {
        "height": "100vh",
        "width": "100vw",
        "border": "none",
        "display": "block",
        "pointerEvents": "none",
    }
    iframe = kdwidgets.Iframe("http://127.0.0.1:3247", False)
    iframe.layout = iframe_layout
    iframe.style = iframe_style
    server = kdwidgets.Server()
    server.add_widget(iframe)

    target = np.array([0.0, 0.0])
    def on_mouse_move(msg):
        if "x" in msg and "y" in msg:
            target[0] = msg["x"] * 25.0
            target[1] = -msg["y"] * 25.0
            env.env_method("set_pointer_pos", target)
            

    iframe.register_callback("mouse_move", on_mouse_move)

    obs = env.reset()
    try:
        while True:
            action, _states = model.predict(obs, deterministic=True)
            obs, reward, terminated, info = env.step(action)
    except KeyboardInterrupt:
        print("Exiting loop on Ctrl+C")

if __name__ == "__main__":
    main()