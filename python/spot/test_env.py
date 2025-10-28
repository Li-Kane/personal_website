from spot import SpotEnv

def main():
    env = SpotEnv(port=3248, render_mode="human")
    env.reset()
    input("Press Enter to exit...")
    env.step()

if __name__ == "__main__":
    main()