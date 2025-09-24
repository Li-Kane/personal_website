from spot import SpotEnv

def main():
    env = SpotEnv(render_mode="human", port=2555)
    input("Press Enter to run simulation...")
    env.step()
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()