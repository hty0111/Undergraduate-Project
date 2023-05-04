# 毕设

基于协作任务的多智能体导航规划任务

### 版本迭代

| 版本   | 内容              | 日期        | 测试结果           |
|------|-----------------|-----------|----------------|
| v1.0 | 完成整体训练流程        | 2023.3.11 |                |
| v1.1 | 增加障碍物           | 2023.3.21 |                |
| v1.2 | 训练带有障碍物的地图      | 2023.3.30 |                |
| v1.3 | 去除障碍物后的训练       | 2023.4.17 | 有明显训练痕迹        |
| v1.4 | 避免已完成智能体计入奖励    | 2023.4.20 | 收敛奖励更高，但波动略大   |
| v1.5 | 修改终点为固定间隔       | 2023.4.21 | 波动更大，效果不如前两个版本 |
| v1.6 | 修改起点和终点都随机      | 2023.4.23 | 完全没效果          |
| v2.0 | 修复两个大bug，回到最初版本 | 2023.4.24 | 噶了             |
| v2.1 | 起点和终点都固定        | 2023.4.25 | 嘎              |
| v2.2 | 起点和终点都随机        | 2023.4.25 | 嘎              |
| v2.3 | 降采样             | 2023.4.25 | 嘎              |
| v2.4 | 升采样             | 2023.4.25 | 嘎              |
| v3.0 | 修复reward buffer | 2023.5.4  |                |


### TODO

- [x] 修改起点为随机
- [ ] 障碍物改成相对坐标
- [ ] reward增加总时间和速度
- [ ] 可视化step的连续过程
- [ ] 位置统一到[-1, 1]
- [x] 坐标系转换与速度无关
- [x] 起点均匀按序分布
- [x] 终点不重合
- [ ] 修改lattice采样模式
- [x] 添加障碍物
- [x] agent结束时reward取消计算
- [ ] step过程中也加入碰撞检测
- [x] 终点位置改为固定间隔
- [ ] 将base_env中的lattice部分移植到entity中
- [ ] 整理utils