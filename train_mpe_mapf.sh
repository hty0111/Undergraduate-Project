#!/bin/sh
env="MPE"
scenario="mapf"
num_landmarks=10
num_agents=10
num_obstacles=20
algo="mappo" #"rmappo" "ippo"
exp="train_obs"
seed_max=1

echo "env is ${env}, scenario is ${scenario}, algo is ${algo}, exp is ${exp}, max seed is ${seed_max}"
for seed in `seq ${seed_max}`;
do
    echo "seed is ${seed}:"
    CUDA_VISIBLE_DEVICES=0 PYTHONPATH=./ python ./scripts/train_mpe.py --env_name ${env} --algorithm_name ${algo} --experiment_name ${exp} \
    --scenario_name ${scenario} --num_agents ${num_agents} --num_landmarks ${num_landmarks} --num_obstacles ${num_obstacles} --seed ${seed} \
    --n_training_threads 1 --n_rollout_threads 64 -num_mini_batch 1 --episode_length 25 --num_env_steps 20000000 --ppo_epoch 10 --use_ReLU \
    --gain 0.01 --lr 7e-4 --critic_lr 7e-4
done
