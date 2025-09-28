# 贪吃蛇游戏

这是一个使用 Python `curses` 库编写的终端版贪吃蛇。

## 运行方法

1. 确保本机安装了 Python 3。
2. 在仓库根目录下执行：

   ```bash
   python -m src.snake
   ```

3. 使用方向键控制蛇移动，按 `q` 键退出游戏。

> 注意：Windows 下运行需要先安装 [windows-curses](https://pypi.org/project/windows-curses/)。

## 游戏规则

- 撞到墙壁或蛇身时游戏结束。
- 吃到食物会增长蛇身长度并增加分数。
- 若终端窗口小于 20×40，程序会提示调整窗口大小。
