import os
print("Current working directory:", os.getcwd())

import tensorflow as tf
import numpy as np

from tf_agents.environments import py_environment
from tf_agents.environments import tf_py_environment
from tf_agents.specs import array_spec
from tf_agents.trajectories import time_step as ts

from tf_agents.networks import q_network
from tf_agents.agents.dqn import dqn_agent
from tf_agents.utils import common

from tf_agents.replay_buffers import tf_uniform_replay_buffer
from tf_agents.trajectories import trajectory

# =============================================================================
# 1. 커스텀 캘린더 환경 정의 (예시)
# =============================================================================
class CalendarEnv(py_environment.PyEnvironment):
    """
    이 환경은 '일정의 상태'를 5차원 벡터로 표현하고,
    세 가지 액션(0: 일정 값 증가, 1: 감소, 2: 변화 없음)을 통해
    상태를 목표 상태([5, 5, 5, 5, 5])에 가깝게 만드는 문제로 구성되어 있습니다.
    """
    def __init__(self):
        # 액션 스펙: 0, 1, 2 중 하나 (ex. 일정 조정 방법)
        self._action_spec = array_spec.BoundedArraySpec(
            shape=(), dtype=np.int32, minimum=0, maximum=2, name='action')
        # 관측(observation) 스펙: 5차원 벡터 (일정의 여러 특성)
        self._observation_spec = array_spec.BoundedArraySpec(
            shape=(5,), dtype=np.float32, minimum=0, maximum=10, name='observation')
        # 초기 상태: 0~10 사이의 랜덤 값
        self._state = np.random.uniform(low=0, high=10, size=(5,)).astype(np.float32)
        self._episode_ended = False
        # 목표 상태 (예시로 모든 특성이 5인 상태)
        self._target = np.array([5.0, 5.0, 5.0, 5.0, 5.0], dtype=np.float32)

    def action_spec(self):
        return self._action_spec

    def observation_spec(self):
        return self._observation_spec

    def _reset(self):
        self._state = np.random.uniform(low=0, high=10, size=(5,)).astype(np.float32)
        self._episode_ended = False
        return ts.restart(self._state)

    def _step(self, action):
        if self._episode_ended:
            return self.reset()

        # 간단한 규칙: 
        # action 0 -> 각 특성에 0.5를 더하고, 
        # action 1 -> 각 특성에서 0.5를 빼며,
        # action 2 -> 상태 변화 없음
        if action == 0:
            self._state = np.clip(self._state + 0.5, 0, 10)
        elif action == 1:
            self._state = np.clip(self._state - 0.5, 0, 10)
        else:
            self._state = self._state

        # 보상은 목표 상태와의 유클리드 거리의 음수로 정의 (목표에 가까울수록 보상이 높음)
        reward = -np.linalg.norm(self._state - self._target)
        
        # 상태가 목표에 충분히 가까워지면 에피소드 종료
        if np.allclose(self._state, self._target, atol=0.5):
            self._episode_ended = True
            return ts.termination(self._state, reward)
        else:
            return ts.transition(self._state, reward=reward, discount=0.9)

# =============================================================================
# 2. 환경 및 에이전트 준비
# =============================================================================

# 파이썬 환경과 TF 환경으로 감싸기
train_py_env = CalendarEnv()
eval_py_env = CalendarEnv()

train_env = tf_py_environment.TFPyEnvironment(train_py_env)
eval_env = tf_py_environment.TFPyEnvironment(eval_py_env)

# Q-Network 정의 (여기서는 2개의 완전 연결 층 사용)
fc_layer_params = (64, 64)
q_net = q_network.QNetwork(
    train_env.observation_spec(),
    train_env.action_spec(),
    fc_layer_params=fc_layer_params)

# DQN 에이전트 생성
optimizer = tf.keras.optimizers.Adam(learning_rate=1e-3)
global_step = tf.Variable(0, dtype=tf.int64)

agent = dqn_agent.DqnAgent(
    train_env.time_step_spec(),
    train_env.action_spec(),
    q_network=q_net,
    optimizer=optimizer,
    td_errors_loss_fn=common.element_wise_squared_loss,
    train_step_counter=global_step)
agent.initialize()

# =============================================================================
# 3. 리플레이 버퍼 및 데이터 수집
# =============================================================================

# 리플레이 버퍼 설정 (에이전트가 수집한 경험 저장)
replay_buffer = tf_uniform_replay_buffer.TFUniformReplayBuffer(
    data_spec=agent.collect_data_spec,
    batch_size=train_env.batch_size,
    max_length=10000)

def collect_step(environment, policy, buffer):
    """현재 상태에서 액션을 취하고, 그 결과를 리플레이 버퍼에 저장"""
    time_step = environment.current_time_step()
    action_step = policy.action(time_step)
    next_time_step = environment.step(action_step.action)
    traj = trajectory.from_transition(time_step, action_step, next_time_step)
    buffer.add_batch(traj)

# 초기 데이터 수집 (에이전트 수집 정책 사용)
for _ in range(100):
    collect_step(train_env, agent.collect_policy, replay_buffer)

# 리플레이 버퍼에서 배치 데이터를 샘플링하는 Dataset 생성
dataset = replay_buffer.as_dataset(
    num_parallel_calls=3,
    sample_batch_size=64,
    num_steps=2).prefetch(3)
iterator = iter(dataset)

# =============================================================================
# 4. 학습 루프
# =============================================================================

num_iterations = 2000

for _ in range(num_iterations):
    # 환경과 상호작용하며 경험 수집
    collect_step(train_env, agent.collect_policy, replay_buffer)
    
    # 리플레이 버퍼에서 배치를 샘플링하여 에이전트 학습
    experience, unused_info = next(iterator)
    train_loss = agent.train(experience).loss

    if global_step.numpy() % 200 == 0:
        print('step = {0}: loss = {1}'.format(global_step.numpy(), train_loss))

print('Training complete.')
