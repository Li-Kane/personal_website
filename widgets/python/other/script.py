from widgets.python.env import ATRVEnv
import gymnasium as gym
import numpy as np

gym.register(
    id="kdFlex-ATRVjr",
    entry_point=ATRVEnv,
    max_episode_steps=200,
)

def main():
    env = gym.make("kdFlex-ATRVjr", port=3246, render_mode="human", sync_real_time=True)
    while True:
        user_input = input("Run env (or 'q' to quit): ")
        if user_input.lower() == 'q':
            break
        obs, info = env.reset()
        while True:
            user_input = input("Enter action (or 'q' to quit): ")
            action = np.array([0.0, 0.0])
            if user_input.lower() == 'q':
                break
            elif user_input == 'w':
                action = np.array([1.0, 1.0])
            elif user_input == 's':
                action = np.array([-1.0, -1.0])
            elif user_input == 'a':
                action = np.array([-1.0, 1.0])
            elif user_input == 'd':
                action = np.array([1.0, -1.0])

            obs, reward, terminated, truncated, info = env.step(action)

if __name__ == "__main__":
    main()