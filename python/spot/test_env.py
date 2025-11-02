from spot import SpotEnv
import gymnasium as gym
import numpy as np

def main():
    # setup simulation
    env = SpotEnv(port=3247, render_mode="human", sync_real_time=True)
    # if they press enter, reset the environment, q to quit
    while True:
        str_input = input("Press Enter to reset the environment, or 'q' to quit: ")
        if str_input.lower() == 'q':
            break
        else:
            env.reset()
        action = np.array([0.0, 0.0, 0.0])
        while True:
            # w a s d to move the robot, q to quit
            action_input = input()
            if action_input.lower() == 'q':
                break
            elif action_input.lower() == 'w':
                action = np.array([1.0, 0.0, 0.0])
            elif action_input.lower() == 's':
                action = np.array([-1.0, 0.0, 0.0])
            elif action_input.lower() == 'a':
                action = np.array([0.0, 0.0, 0.5])
            elif action_input.lower() == 'd':
                action = np.array([0.0, 0.0, -0.5])
            elif action_input.lower() == "p":
                action = np.array([0.0, 0.0, 0.0])
            env.step(action)

if __name__ == "__main__":
    main()