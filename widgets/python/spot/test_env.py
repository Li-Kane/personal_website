from spot import SpotEnv

def main():
    env = SpotEnv()
    while True:
        # take in keyboard input, if enter, reset else if q, quit
        user_input = input("Press Enter to reset the environment or 'q' to quit: ")
        if user_input.lower() == 'q':
            env.close()
            break
        obs = env.reset()
        while True:
            user_input = input("Enter command (w/a/s/d/r/t for movement, q to quit, e to reset): ")
            if user_input.lower() == 'q':
                env.close()
                return
            elif user_input.lower() == 'e':
                break
            elif user_input.lower() == 'w':
                action = [2, 0, 0]  # forward
            elif user_input.lower() == 's':
                action = [-2, 0, 0]  # backward
            elif user_input.lower() == 'a':
                action = [0, 1, 0]  # left
            elif user_input.lower() == 'd':
                action = [0, -1, 0]  # right
            elif user_input.lower() == 'r':
                action = [0, 0, 1]  # rotate counterclockwise
            elif user_input.lower() == 't':
                action = [0, 0, -1]  # rotate clockwise
            else:
                action = [0, 0, 0]  # no movement
            obs, reward, done, terminated, info = env.step()

if __name__ == "__main__":
    main()