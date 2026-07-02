# hand_SDK
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Python](https://img.shields.io/badge/Python-3.7%2B-blue.svg)
![Build](https://img.shields.io/github/actions/workflow/status/YounG-Z416/hand_SDK/你的工作流文件名.yml?branch=main)
![Coverage](https://codecov.io/gh/YounG-Z416/hand_SDK/branch/main/graph/badge.svg)

A unified control module for Stellarobot dexterous hands, supporting multiple hand interfaces including Gaia, Pantheon, and more. Providing both high‑level abstraction and low‑level control primitives, making it suitable for robotics research, education, and industrial applications.

# SDK
<table border="1">
    <tr>
        <th>Languege</th>
        <th>Install</th>
        <th>Docs</th>
        <th>Example</th>
    </tr>
    <tr>
        <td><strong>Python</strong></td>
        <td>pip install handsdk</td>
        <td><a href="https://qcnqdkti44v2.feishu.cn/wiki/FoLuwaO3ziOTSZkzplHcStIxnm7">hand_SDK Development Guidelines</a></td>
        <td>
            <a href="example/gaiahand_example">GaiaHand</a>
            <a href="pqntheonhand_example">PantheonHand</a>
        </td>
    </tr>
</table>

# SDK Structure
```
hand/
├── hand/
│   ├── __init__.py          # 模块入口
│   ├── core.py              # 核心抽象类和适配器
│   ├── gaiahand/            # Gaia手部实现
│   │   ├── gaia_hand.py     # Gaia手部适配器
│   │   ├── motor.py         # 电机控制
│   │   └── hand_mappings.py # 映射关系
│   ├── pantheonhand/        # Pantheon手部实现
│   │   ├── pantheon_hand.py # Pantheon手部适配器
│   │   └── can_utils/       # CAN通信工具
│   └── utils/               # 工具函数
│       └── serial_utils.py  # 串口工具
├── example/                 # 示例代码
├── docs/                    # 文档
├── tests/                   # 测试代码
└── setup.py                 # 安装配置
```

# Documentation
For more detailed documentation,  see [https://qcnqdkti44v2.feishu.cn/wiki/FoLuwaO3ziOTSZkzplHcStIxnm7](hand_SDK Development Guidelines)

# Contact
Project Homepage: https://gitee.com/stellarrobot/handsdk
Feedback: https://gitee.com/stellarrobot/handsdk/issues
Email: zhiqiangtan89@gmail.com
Documentation: https://hand-control.readthedocs.io/

# License
This project is licensed under the MIT License , see [LICENSE](LICENSE) for details.
