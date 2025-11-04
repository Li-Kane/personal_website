from spot import SpotEnv
import gymnasium as gym
import numpy as np

def main():
    # setup simulation
    env = SpotEnv(port=3247, render_mode="human", sync_real_time=True)
    # if they press enter, reset the environment, q to quit
    env.reset()
    action = np.array([1.0, 0.0, 2.0])
    for _ in range(100):
        env.step(action)
    action = np.array([1.0, 0.0, 0.0])
    for _ in range(1000):
        env.step(action)
    avg_step_time = np.mean(env._step_times)
    avg_obs_time = np.mean(env._observation_times)
    avg_advance_time = np.mean(env._advance_times)
    avg_apply_forces_time = np.mean(env._af_per_step)
    print(f"Average step time: {avg_step_time*1000:.2f} ms")
    print(f"Average observation time: {avg_obs_time*1000:.2f} ms")
    print(f"Average advance time: {avg_advance_time*1000:.2f} ms")
    print(f"Average apply forces time per call: {avg_apply_forces_time*1000:.4f} ms")

if __name__ == "__main__":
    main()