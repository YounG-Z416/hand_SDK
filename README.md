# hand_SDK
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Python](https://img.shields.io/badge/Python-3.7%2B-blue.svg)
![Coverage](https://codecov.io/gh/YounG-Z416/hand_SDK/branch/main/graph/badge.svg)

A unified control module for Stellarobot dexterous hands, supporting multiple hand interfaces including Gaia, Pantheon, and more. Providing both high‑level abstraction and low‑level control primitives, making it suitable for robotics research, education, and industrial applications.

# SDK

| Language | Install | Docs | Example |
|----------|---------|------|---------|
| Python | `pip install handsdk` | [hand_SDK Development Guidelines](https://qcnqdkti44v2.feishu.cn/wiki/FoLuwaO3ziOTSZkzplHcStIxnm7)) | [GaiaHand](./example/gaiahand_example.py) [PantheonHand](./example/pantheonhand_example.py) |

# SDK Structure
```
hand/
├── hand/
│   ├── __init__.py          # Module Entry
│   ├── core.py              # Core Abstract Classes and Adapters
│   ├── gaiahand/            # GaiaHand Implementation
│   │   ├── gaia_hand.py     # GaiaHand Adapter
│   │   ├── motor.py         # Motor Control
│   │   └── hand_mappings.py # Mapping
│   ├── pantheonhand/        # PantheonHand Implementation
│   │   ├── pantheon_hand.py # PantheonHand Adapter
│   │   └── can_utils/       # CAN Communication Utilities
│   └── utils/               # Utility Functions
│       └── serial_utils.py  # Serial Port Utilities
├── example/                 # Examples
├── docs/                    # Documentation
├── tests/                   # Tests
└── setup.py                 # Installation
```

# Documentation
For more detailed documentation,  see [hand_SDK Development Guidelines](https://qcnqdkti44v2.feishu.cn/wiki/FoLuwaO3ziOTSZkzplHcStIxnm7)

# Contact
Project Homepage: [https://gitee.com/stellarrobot/handsdk](https://gitee.com/stellarrobot/handsdk)

Feedback: [https://gitee.com/stellarrobot/handsdk/issues](https://gitee.com/stellarrobot/handsdk/issues)

Email: [zhiqiangtan89@gmail.com](zhiqiangtan89@gmail.com)

Documentation: [https://hand-control.readthedocs.io/](https://hand-control.readthedocs.io/)

# License
This project is licensed under the MIT License , see [LICENSE](LICENSE) for details.
