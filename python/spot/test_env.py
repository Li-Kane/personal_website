from spot import SpotEnv
import gymnasium as gym
import numpy as np
# from gymnasium.utils.env_checker import check_env

gym.register(
    id="kdFlex-Spot",
    entry_point=SpotEnv,
    max_episode_steps=1000,
)

def main():
    # setup simulation
    env = gym.make("kdFlex-Spot", port=3247, render_mode="human", sync_real_time=True)
    # check_env(env.unwrapped, warn=True)
    # if they press enter, reset the environment, q to quit
    while True:
        str_input = input("Press Enter to reset the environment, or 'q' to quit: ")
        if str_input.lower() == 'q':
            env.close()
            break
        else:
            env.reset()
        # action = 4
        action = np.array([0.0, 0.0, 0.0])
        while True:
            # w a s d to move the robot, q to quit
            action_input = input()
            if action_input.lower() == 'q':
                break
            elif action_input.lower() == 'w':
                # action = 0
                action = np.array([1.0, 0.0, 0.0])
            elif action_input.lower() == 's':
                # action = 1
                action = np.array([-1.0, 0.0, 0.0])
            elif action_input.lower() == 'a':
                # action = 2
                action = np.array([0.5, 0.0, 1.0])
            elif action_input.lower() == 'd':
                # action = 3
                action = np.array([0.5, 0.0, -1.0])
            elif action_input.lower() == "p":
                action = np.array([0.0, 0.0, 0.0])
            obs, reward, done, truncated, info = env.step(action)
            if done:
                print("Episode finished. Resetting environment.")
                break

if __name__ == "__main__":
    main()