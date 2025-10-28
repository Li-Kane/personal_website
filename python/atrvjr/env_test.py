from env import ATRVEnv
import gymnasium as gym
import numpy as np

gym.register(
    id="kdFlex-ATRVjr",
    entry_point=ATRVEnv,
)

def main():
    # setup simulation
    env = gym.make("kdFlex-ATRVjr", port=3247, render_mode="human", sync_real_time=True)
    # if they press enter, reset the environment, q to quit
    while True:
        str_input = input("Press Enter to reset the environment, or 'q' to quit: ")
        if str_input.lower() == 'q':
            break
        else:
            env.reset()
        action = np.array([0.0, 0.0])
        while True:
            # w a s d to move the robot, q to quit
            action_input = input()
            if action_input.lower() == 'q':
                break
            elif action_input.lower() == 'w':
                action = np.array([1.0, 1.0])
            elif action_input.lower() == 's':
                action = np.array([-1.0, -1.0])
            elif action_input.lower() == 'a':
                action = np.array([-1.0, 1.0])
            elif action_input.lower() == 'd':
                action = np.array([1.0, -1.0])
            obs, reward, terminated, truncated, info = env.step(action)
            print("terminated:", terminated, "truncated:", truncated)

if __name__ == "__main__":
    main()