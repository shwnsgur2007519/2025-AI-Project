import numpy as np
import random
import matplotlib.pyplot as plt  # type: ignore

# --------------------------
# 간단한 스케줄링 환경 클래스
# --------------------------
class SimpleScheduleEnv:
    def __init__(self):
        self.num_blocks = 10  # 하루를 10개의 블록으로 나눔
        self.num_tasks = 3    # 일반 일정 3개
        self.total_actions = self.num_tasks + 1  # 마지막은 'DoNothing'
        self.reset()

    def reset(self):
        self.current_block = 0
        self.schedule = [-1] * self.num_blocks
        self.done = False
        return self._get_state()

    def _get_state(self):
        remaining = sum(1 for i in range(self.num_tasks) if i not in self.schedule)
        return np.array([self.current_block, remaining], dtype=np.float32)

    def step(self, action):
        reward = 0
        if self.done:
            return self._get_state(), reward, True, {}

        if action == self.total_actions - 1:  # DoNothing
            reward = 0
        else:
            if self.schedule[self.current_block] != -1 or action in self.schedule:
                reward = -1  # 충돌 or 이미 배정된 task
            else:
                self.schedule[self.current_block] = action
                reward = 1  # 정상 배정

        self.current_block += 1
        if self.current_block >= self.num_blocks:
            self.done = True

        return self._get_state(), reward, self.done, {}

# --------------------------
# 피처 벡터 생성 함수
# --------------------------
def get_feature(state, action, state_dim, action_dim):
    s_feat = state / 10.0  # 정규화
    a_feat = np.eye(action_dim)[action]
    return np.concatenate([s_feat, a_feat])

# --------------------------
# n-step Q-learning 학습
# --------------------------
state_dim = 2
action_dim = 4  # 3 tasks + DoNothing
feature_dim = state_dim + action_dim

w = np.zeros(feature_dim)
gamma = 0.95
alpha = 0.1
n_step = 3
episodes = 200

log = []

for ep in range(episodes):
    env = SimpleScheduleEnv()
    state = env.reset()
    done = False
    memory = []

    total_reward = 0

    while not done:
        # ε-greedy
        epsilon = max(0.1, 1 - ep / 150)
        if random.random() < epsilon:
            action = random.randint(0, action_dim - 1)
        else:
            q_vals = []
            for a in range(action_dim):
                phi = get_feature(state, a, state_dim, action_dim)
                q_vals.append(np.dot(w, phi))
            action = int(np.argmax(q_vals))

        next_state, reward, done, _ = env.step(action)
        memory.append((state, action, reward, next_state))
        total_reward += reward
        state = next_state

        # n-step update
        if len(memory) >= n_step:
            G = 0
            for i in range(n_step):
                G += (gamma ** i) * memory[i][2]
            if not done:
                future_qs = [
                    np.dot(w, get_feature(memory[-1][3], a, state_dim, action_dim))
                    for a in range(action_dim)
                ]
                G += (gamma ** n_step) * max(future_qs)

            s_tau, a_tau, _, _ = memory[0]
            phi_tau = get_feature(s_tau, a_tau, state_dim, action_dim)
            q_hat = np.dot(w, phi_tau)
            w += alpha * (G - q_hat) * phi_tau

            memory.pop(0)

    log.append(total_reward)

# --------------------------
# 학습 결과 시각화
# --------------------------
plt.plot(log)
plt.title("Total reward per episode (n-step Linear Q)")
plt.xlabel("Episode")
plt.ylabel("Total reward")
plt.grid()
plt.show()
