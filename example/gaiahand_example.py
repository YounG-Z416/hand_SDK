#!/usr/bin/env python3
"""
GaiaHand 控制示例文件

⭐ 推荐使用 Gaia20（16关节版本），当前主要维护版本
⚠️ Gaia15（15关节版本）已暂停维护，示例代码仅用于兼容旧代码

功能说明：
- 测试不同手部类型的 move_joints_pos 方法，包括单手和双手模式
- 串口自动检测功能
- 电机平滑等级设置
- 关节位置控制（列表格式和字典格式）
- 手势执行和回零操作
- 错误处理和资源清理
- 日志管理功能（enable_all_logs、disable_all_logs、set_log_level、set_console_only、
  set_file_only、set_both_output、show_log_status、log_controller，可通过 test_log_management() 测试）

波特率配置说明：
- Gaia15: 230400（标准配置）
  - 注意：示例文件中部分测试函数使用了921600，但标准配置应为230400
- Gaia20不带主控板: 230400（默认配置）
- Gaia20带主控板: 921600（高性能配置）

使用说明：
1. 根据您的硬件配置选择合适的波特率
2. 在main()函数中取消注释相应的测试函数来运行测试
3. 默认优先运行Gaia20测试函数
"""

import time
import sys
import os
import math

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hand import create_hand, HandSide
from hand.gaiahand.hand_mappings import FingerType, JointType
from hand.utils.serial_utils import auto_detect_gaia_ports

# 导入日志管理功能
from hand.core import (
    enable_all_logs,
    disable_all_logs,
    set_log_level,
    set_console_only,
    set_file_only,
    set_both_output,
    show_log_status,
    log_controller
)

def set_motor_smooth_level(hand, device_id: int = 255, level: int = 3, description: str = ""):
    """
    设置电机平滑等级的辅助函数
    
    Args:
        hand: 手部控制实例
        device_id: 设备ID，255表示广播所有电机，None表示使用默认值
        level: 平滑等级 (0-5)，数值越大平滑效果越好
        description: 可选的描述信息，用于打印日志
    """
    desc_text = f" ({description})" if description else ""
    print(f"设置电机平滑等级{desc_text}...")
    print(f"  参数: device_id={device_id}, level={level}")
    try:
        hand.config_pos_lpf_lv(device_id=device_id, level=level)
        print(f"电机平滑等级设置成功（device_id={device_id}, level={level}）")
        return True
    except Exception as e:
        print(f"电机平滑等级设置失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_log_management():
    """测试日志管理功能"""
    print("\n" + "=" * 60)
    print("=== 测试日志管理功能 ===")

    # 1. 测试启用所有日志
    print("\n1. 启用所有日志...")
    enable_all_logs()
    print("✅ 已启用所有日志")

    # 2. 测试设置日志级别
    print("\n2. 设置日志级别为 DEBUG...")
    set_log_level('DEBUG')
    print("✅ 已设置日志级别为 DEBUG")

    # 3. 测试不同输出方式
    print("\n3. 测试不同输出方式...")

    print("   - 设置为控制台输出...")
    set_console_only()
    print("   ✅ 已设置为仅控制台输出")

    print("   - 设置为文件输出...")
    set_file_only()
    print("   ✅ 已设置为仅文件输出")

    print("   - 设置为控制台+文件输出...")
    set_both_output()
    print("   ✅ 已设置为控制台+文件输出")

    # 4. 测试禁用所有日志
    print("\n4. 测试禁用所有日志...")
    disable_all_logs()
    print("❌ 已禁用所有日志")

    # 测试禁用日志后的效果 - 这些日志应该不会显示
    print("\n   测试禁用日志后的效果（以下日志应该不会显示）:")
    from hand.core import get_logger
    test_logger = get_logger('test.disable_logs')
    test_logger.info("这条 INFO 日志应该不会显示")
    test_logger.warning("这条 WARNING 日志应该不会显示")
    test_logger.error("这条 ERROR 日志应该不会显示")
    print("   ✅ 禁用日志测试完成")

    # 5. 测试特定脚本的日志控制
    print("\n5. 测试特定脚本的日志控制...")
    log_controller.set_script_logging('gaiahand.motor', enabled=True, level='WARNING')
    print("✅ 已设置 gaiahand.motor 为 WARNING 级别")

    # 6. 显示当前日志状态
    print("\n6. 当前日志状态:")
    show_log_status()

    # 7. 重新启用日志以便后续测试
    print("\n7. 重新启用日志以便后续测试...")
    enable_all_logs()
    set_log_level('INFO')
    set_both_output()
    print("✅ 已重新启用日志")


def detect_serial_ports():
    """
    检测可用的串口
    
    Returns:
        dict: 串口配置信息
    """
    try:
        print("正在检测可用串口...")
        ports_config = auto_detect_gaia_ports()
        
        if not ports_config or not ports_config['available']:
            print("未检测到可用串口，请检查硬件连接")
            return None
        
        return ports_config
        
    except Exception as e:
        print(f"串口检测失败: {e}")
        return None


def test_gaia20_hand_create_hand(ports_config):
    """
    测试 GaiaHand20 的创建方式
    
    列举具体的创建手的方式（单手/双手、串口/SLCAN、带/不带主控板等）。
    """
    print("\n" + "=" * 60)
    print("=== GaiaHand20 创建方式与状态获取示例 ===")
    print("=" * 60)
    
    # ==================== 一、创建手的方式 ====================
    print("\n【一、创建 GaiaHand20 的多种方式】\n")
    print("串口说明: Windows 为 COM4/COM5 等，Linux 为 /dev/ttyUSB0、/dev/ttyACM0 等")
    print("推荐: 使用 ports_config = auto_detect_gaia_ports() 自动检测，port=ports_config['right']\n")
    
    print("1. 右手单手 - 串口直连（不带主控板，波特率 230400）")
    print("   # 使用 ports_config（推荐）:")
    print("   hand = create_hand('gaia20', 'right', port=ports_config['right'], baudrate=230400)")
    print("   # 或指定串口: Windows port='COM4'，Linux port='/dev/ttyUSB0'")
    print()
    
    print("2. 右手单手 - 串口直连（带主控板，波特率 921600）")
    print("   hand = create_hand('gaia20', 'right', port=ports_config['right'], baudrate=921600, has_main_board=True)")
    print("   # 或指定: port='COM4' (Win) / port='/dev/ttyUSB0' (Linux)")
    print()
    
    print("3. 右手单手 - SLCAN/CAN 模式（默认带主控板）")
    print("   hand = create_hand('gaia20', 'right', port=ports_config['right'], use_slcan=True)")
    print("   # 或指定: port='COM6' (Win) / port='/dev/ttyUSB0' (Linux)")
    print("   # 可选: slcan_tty_baudrate=115200, slcan_arbitration_bitrate=1000000, slcan_data_bitrate=2000000")
    print()
    
    print("4. 左手单手 - 串口直连")
    print("   hand = create_hand('gaia20', 'left', port=ports_config['left'], baudrate=230400)")
    print("   # 或指定: port='COM5' (Win) / port='/dev/ttyUSB1' (Linux)")
    print()
    
    print("5. 双手模式 - 串口直连")
    print("   hand = create_hand('gaia20', 'double', left_port=ports_config['left'], right_port=ports_config['right'], baudrate=230400)")
    print("   # 或指定: left_port='COM5', right_port='COM4' (Win) / left_port='/dev/ttyUSB1', right_port='/dev/ttyUSB0' (Linux)")
    print("   # 带主控板: baudrate=921600")
    print()
    
    print("6. 双手模式 - SLCAN/CAN（默认带主控板）")
    print("   hand = create_hand('gaia20', 'double', left_port=ports_config['left'], right_port=ports_config['right'], use_slcan=True)")
    print("   # 或指定: left_port='COM5', right_port='COM4' (Win) / left_port='/dev/ttyUSB1', right_port='/dev/ttyUSB0' (Linux)")
    print()


def test_gaia20_hand_get_status(ports_config):
    """
    测试 GaiaHand20 的状态获取
    
    演示：连接状态、关节位置、单个电机状态、所有电机状态。
    """
    print("\n" + "=" * 60)
    print("=== GaiaHand20 状态获取测试 ===")
    print("=" * 60)
    
    if not ports_config or not ports_config.get('right'):
        print("未检测到右手串口，跳过状态获取测试")
        return
    
    hand = None
    try:
        hand = create_hand("gaia20", "right", port=ports_config['right'], baudrate=230400)
        
        print(f"已创建实例: hand_type={hand.hand_type.value}, hand_side={hand.hand_side_name}")
        print(f"连接前 is_connected(): {hand.is_connected()}")
        
        if not hand.connect():
            print("连接失败，请检查串口与硬件")
            return
        
        print(f"连接成功 (串口: {ports_config['right']})")
        print(f"连接后 is_connected(): {hand.is_connected()}")
        
        # 上使能
        hand.enable_all_motors_broadcast(True)
        time.sleep(0.3)
        
        # 1. 获取关节位置（异步）
        print("\n--- 1. 关节位置（异步） ---")
        positions = hand.get_joint_positions(sync=False)
        if positions:
            print(f"共 {len(positions)} 个关节")
            print(f"  前5个(弧度): {[f'{p:.3f}' if p is not None else 'None' for p in positions[:5]]}")
            print(f"  前5个(度):   {[f'{math.degrees(p):.1f}°' if p is not None else 'None' for p in positions[:5]]}")
        
        # 2. 获取关节位置（同步）
        print("\n--- 2. 关节位置（同步） ---")
        positions_sync = hand.get_joint_positions(sync=True, timeout=0.1)
        if positions_sync:
            print(f"共 {len(positions_sync)} 个关节")
            print(f"  前5个(度): {[f'{math.degrees(p):.1f}°' if p is not None else 'None' for p in positions_sync[:5]]}")
        
        # 3. 获取单个电机状态
        print("\n--- 3. 单个电机状态（电机1） ---")
        status_1 = hand.get_motor_status(motor_id=1, sync=True, timeout=0.5)
        print(f"online={status_1.get('online')}, angle={status_1.get('angle')}°, fsm_state={status_1.get('fsm_state')}, "
              f"temp={status_1.get('temp')}°C, bus_voltage={status_1.get('bus_voltage')}V")
        
        # 4. 获取所有电机状态（在线/离线）
        print("\n--- 4. 所有电机状态（在线/离线） ---")
        all_status = hand.get_motor_status(motor_id=None, sync=True, timeout=2.0)
        if isinstance(all_status, dict) and 1 in all_status:
            v = all_status[1]
            if isinstance(v, dict):
                online_count = sum(1 for s in all_status.values() if isinstance(s, dict) and s.get('online'))
            else:
                online_count = sum(1 for s in all_status.values() if s)
            print(f"共 {len(all_status)} 个电机, 在线 {online_count} 个")
        
        hand.enable_all_motors_broadcast(False)
        hand.close()
        print("\n状态获取测试完成")
            
    except Exception as e:
        print(f"状态获取出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if hand and hasattr(hand, 'close'):
            try:
                hand.close()
            except Exception:
                pass


def test_gaia20_hand_joint_limits(ports_config, connect_for_motion: bool = False):
    """
    测试 GaiaHand20 关节限位相关接口。

    默认只演示限位表查询、开关状态、临时设置和恢复默认，不连接硬件、不发送运动指令。
    如需验证超限夹紧后的真实下发效果，可显式传入 connect_for_motion=True。

    关节限位单位均为弧度(rad)。
    """
    print("\n" + "=" * 60)
    print("=== GaiaHand20 关节限位接口示例 ===")
    print("=" * 60)

    if not ports_config or not ports_config.get('right'):
        print("未检测到右手串口，仍可使用示例串口名创建对象并演示非连接接口")

    port = ports_config.get('right') if ports_config else None
    port = port or "COM0"
    hand = None

    try:
        # joint_limit_enabled 默认就是 True，这里显式写出方便查看用法。
        hand = create_hand(
            "gaia20",
            "right",
            port=port,
            baudrate=230400,
            joint_limit_enabled=True,
        )

        print(f"已创建实例: hand_type={hand.hand_type.value}, hand_side={hand.hand_side_name}")
        print(f"HandSDK关节限位默认状态: {hand.is_joint_limit_enabled()}")

        # 1. 查询单个关节限位
        print("\n--- 1. 查询单个关节限位 ---")
        thumb_j1_limit = hand.get_joint_limit(FingerType.THUMB, JointType.JOINT_1)
        print(f"右手拇指 JOINT1 限位(rad): {thumb_j1_limit}")
        if thumb_j1_limit:
            print(
                "右手拇指 JOINT1 限位(deg): "
                f"({math.degrees(thumb_j1_limit[0]):.1f}, {math.degrees(thumb_j1_limit[1]):.1f})"
            )

        # 2. 查询整张生效限位表
        print("\n--- 2. 查询当前生效限位表 ---")
        limits = hand.get_joint_limits()
        print(f"手指列表: {list(limits.keys())}")
        print(f"thumb: {limits.get('thumb')}")

        # 3. 开启/关闭 HandSDK 关节限位
        print("\n--- 3. 开启/关闭 HandSDK 关节限位 ---")
        hand.disable_joint_limit()
        print(f"关闭后: {hand.is_joint_limit_enabled()}")
        hand.enable_joint_limit()
        print(f"重新开启后: {hand.is_joint_limit_enabled()}")

        # 4. 临时设置单个关节限位
        print("\n--- 4. 临时设置单个关节限位 ---")
        original_limit = hand.get_joint_limit(FingerType.THUMB, JointType.JOINT_1)
        hand.set_joint_limit(FingerType.THUMB, JointType.JOINT_1, -0.1, 0.1)
        print(f"临时设置后 thumb JOINT1: {hand.get_joint_limit(FingerType.THUMB, JointType.JOINT_1)}")
        hand.reset_joint_limits(FingerType.THUMB, JointType.JOINT_1)
        print(f"恢复单关节默认后 thumb JOINT1: {hand.get_joint_limit(FingerType.THUMB, JointType.JOINT_1)}")
        print(f"原始默认值: {original_limit}")

        # 5. 临时批量设置限位，支持字符串 JOINT1 和枚举 JointType 两种写法
        print("\n--- 5. 临时批量设置关节限位 ---")
        hand.set_joint_limits({
            "thumb": {
                "JOINT1": (-0.2, 0.2),
                JointType.JOINT_2: (-0.3, 0.3),
            },
            FingerType.INDEX: {
                "JOINT1": (-0.15, 0.15),
            },
        })
        print(f"批量设置后 thumb: {hand.get_joint_limits().get('thumb')}")
        print(f"批量设置后 index JOINT1: {hand.get_joint_limit(FingerType.INDEX, JointType.JOINT_1)}")
        hand.reset_joint_limits()
        print(f"全部恢复默认后 thumb: {hand.get_joint_limits().get('thumb')}")

        # 6. 一次性修改所有关节限位
        print("\n--- 6. 一次性修改所有关节限位 ---")
        default_limits = hand.get_joint_limits()
        all_joint_limits = {}
        for finger, joints in default_limits.items():
            all_joint_limits[finger] = {}
            for joint, (lower, upper) in joints.items():
                # 示例：把所有关节的临时限位收窄到默认范围和 [-0.25, 0.25] 的交集。
                # 实际项目中可把这里替换成标定/配置文件生成的整表限位。
                new_lower = max(lower, -0.25)
                new_upper = min(upper, 0.25)
                all_joint_limits[finger][joint] = (new_lower, new_upper)

        hand.set_joint_limits(all_joint_limits)
        total_joint_count = sum(len(joints) for joints in all_joint_limits.values())
        print(f"已一次性临时修改 {total_joint_count} 个关节限位")
        print(f"整表设置后 thumb: {hand.get_joint_limits().get('thumb')}")
        print(f"整表设置后 little: {hand.get_joint_limits().get('little')}")
        hand.reset_joint_limits()
        print(f"整表恢复默认后 thumb: {hand.get_joint_limits().get('thumb')}")

        # 7. 创建时关闭限位
        print("\n--- 7. 创建时关闭关节限位 ---")
        hand_no_limit = create_hand(
            "gaia20",
            "right",
            port=port,
            baudrate=230400,
            joint_limit_enabled=False,
        )
        print(f"joint_limit_enabled=False 创建后状态: {hand_no_limit.is_joint_limit_enabled()}")
        if hasattr(hand_no_limit, 'close'):
            hand_no_limit.close()

        # 8. 可选：连接硬件后验证超限夹紧
        print("\n--- 8. 可选：连接硬件验证超限夹紧 ---")
        if not connect_for_motion:
            print("默认跳过真实运动示例。需要时调用 test_gaia20_hand_joint_limits(ports_config, connect_for_motion=True)")
            return

        print("准备连接硬件并执行一个超限指令示例...")
        if not hand.connect():
            print("连接失败，跳过真实运动示例")
            return

        hand.enable_all_motors_broadcast(True)
        time.sleep(0.5)
        hand.set_joint_limit(FingerType.THUMB, JointType.JOINT_1, -0.1, 0.1)
        print("发送 thumb JOINT1 = 1.0 rad，实际会被 HandSDK 夹紧到 0.1 rad 并记录 warning")
        hand.set_joint_angle(FingerType.THUMB, JointType.JOINT_1, 1.0, speed=0.3)
        time.sleep(1.0)
        hand.reset_joint_limits()
        hand.hand_zero()
        time.sleep(1.0)

    except Exception as e:
        print(f"GaiaHand20 关节限位示例失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if hand and hasattr(hand, 'is_connected') and hand.is_connected():
            try:
                hand.enable_all_motors_broadcast(False)
                hand.close()
            except Exception:
                pass


def test_gaia20_hand_get_joint_positions(ports_config, tests_to_run=None):
    """
    测试 GaiaHand20 的 get_joint_positions 功能（16关节版本）
    
    ⭐ 推荐使用：Gaia20当前主要维护版本
    
    波特率配置：230400（不带主控板版本）
    
    Args:
        ports_config: 串口配置字典
        tests_to_run: 要运行的测试列表，例如 [1, 2, 3] 表示只运行测试1、2、3
                     如果为 None 或空列表，则运行所有测试（默认行为）
                     可用测试编号：1-7
                     测试1：获取所有关节位置（异步模式）
                     测试2：获取所有关节位置（同步模式）
                     测试3：设置位置后获取位置验证
                     测试4：多次获取位置（观察数据变化）
                     测试5：获取指定关节位置
                     测试6：回零后获取位置
                     测试7：从0位置插补到目标位置，每步获取位置
    """
    print("\n=== 测试 GaiaHand20 get_joint_positions 功能（16关节版本）===")
    
    # 如果没有指定测试列表，则运行所有测试
    if tests_to_run is None:
        tests_to_run = [7]
    elif not tests_to_run:
        tests_to_run = [1, 2, 3, 4, 5, 6, 7]
    
    # 显示将要运行的测试
    print(f"将要运行的测试: {tests_to_run}")
    
    if not ports_config or not ports_config['right']:
        print("未找到可用的右手串口，跳过获取位置测试")
        return
    
    hand = None
    try:
        # 创建右手 GaiaHand20 实例
        # ⭐ 波特率配置说明：
        # - 带主控板版本：baudrate=921600（高性能配置）
        # - 不带主控板版本：baudrate=230400（默认配置）
        # hand = create_hand("gaia20", "right", port=ports_config['right'], baudrate=921600, has_main_board=True)  # 带主控板版本，自动识别端口号
        # hand = create_hand("gaia20", "right", port=ports_config['right'], baudrate=230400)  # 不带主控板版本，自动识别端口号
        # hand = create_hand("gaia20", "right", port='COM12', baudrate=921600, has_main_board=True)  # 串口，自配端口号
        # hand = create_hand("gaia20", "right", port='COM8', baudrate=921600, has_main_board=True)  # 串口，自配端口号，带主控板

        # hand = create_hand("gaia20", "right", port=ports_config['right'], use_slcan=True)   # SLCAN模式，默认带主控板
        hand = create_hand("gaia20", "right", port='COM6', use_slcan=True, has_main_board=True)   # SLCAN模式，带主控板


        if hand.connect():
            print(f"GaiaHand20 连接成功 (串口: {ports_config['right']})")
            
            # 设置电机平滑等级（device_id=255表示广播所有电机，level=3）
            # 设置电机平滑等级（device_id=255表示广播所有电机，level=0）
            # 平滑等级范围：0-5，level=0表示关闭平滑
            set_motor_smooth_level(hand, device_id=255, level=3, description="测试关闭平滑")
            
            # 等待设置生效
            # time.sleep(0.5)
            
            # 上使能所有关节
            print("上使能所有关节...")
            enable_success = hand.enable_all_motors_broadcast(True)
            print(f"上使能结果: {'成功' if enable_success else '失败'}")
            
            if not enable_success:
                print("上使能失败，无法继续测试")
                return
            
            # 等待使能稳定
            time.sleep(0.5)
            
            # 测试1：获取所有关节位置（异步模式），建议使用异步模式
            if 1 in tests_to_run:
                print("\n--- 测试1：获取所有关节位置（异步模式） ---")
                all_positions = hand.get_joint_positions(sync=False)
                print(f"所有关节位置（异步）: {all_positions}")
                print(f"位置数据类型: {type(all_positions)}")
                if isinstance(all_positions, (list, tuple)):
                    print(f"位置数据长度: {len(all_positions)}")
                    if len(all_positions) > 0:
                        print(f"前5个关节位置: {all_positions[:5]}")
                        print(f"后5个关节位置: {all_positions[-5:]}")
                time.sleep(1)
            
            # 测试2：获取所有关节位置（同步模式）
            if 2 in tests_to_run:
                print("\n--- 测试2：获取所有关节位置（同步模式） ---")
                all_positions_sync = hand.get_joint_positions(sync=True, timeout=0.1)
                print(f"所有关节位置（同步）: {all_positions_sync}")
                print(f"位置数据类型: {type(all_positions_sync)}")
                if isinstance(all_positions_sync, (list, tuple)):
                    print(f"位置数据长度: {len(all_positions_sync)}")
                    if len(all_positions_sync) > 0:
                        print(f"前5个关节位置: {all_positions_sync[:5]}")
                        print(f"后5个关节位置: {all_positions_sync[-5:]}")
                        # 转换为度数显示
                        print("前5个关节位置（度）: ", [math.degrees(p) if p is not None else None for p in all_positions_sync[:5]])
                time.sleep(0.5)
            
            # 测试3：设置位置后获取位置验证
            if 3 in tests_to_run:
                print("\n--- 测试3：设置位置后获取位置验证 ---")
                # 设置一个已知位置
                target_positions = [
                    # 拇指的4个关节
                    0.0, math.radians(10.0), math.radians(20.0), math.radians(15.0),
                    # 食指的3个关节
                    0.0, math.radians(45.0), math.radians(40.0),
                    # 中指的3个关节
                    0.0, math.radians(45.0), math.radians(45.0),
                    # 无名指的3个关节
                    0.0, math.radians(40.0), math.radians(40.0),
                    # 小指的3个关节
                    0.0, math.radians(45.0), math.radians(45.0)
                ]
                
                print(f"设置目标位置（弧度）: {target_positions[:5]}...")
                success = hand.move_joints_pos(target_positions, speed=0.8, use_broadcast=True)
                print(f"设置位置结果: {'成功' if success else '失败'}")
                
                # 等待运动完成
                time.sleep(2)
                
                # 获取当前位置
                current_positions = hand.get_joint_positions(sync=True, timeout=0.1)
                print(f"当前位置（弧度）: {current_positions}")
                if isinstance(current_positions, (list, tuple)) and len(current_positions) >= 16:
                    print("位置对比（前5个关节）:")
                    for i in range(5):
                        target = target_positions[i] if i < len(target_positions) else None
                        current = current_positions[i] if i < len(current_positions) else None
                        if target is not None and current is not None:
                            diff = abs(target - current)
                            print(f"  关节{i+1}: 目标={math.degrees(target):.2f}°, 当前={math.degrees(current):.2f}°, 误差={math.degrees(diff):.2f}°")
                        else:
                            print(f"  关节{i+1}: 目标={target}, 当前={current}")
                time.sleep(1)
            
            # 测试4：多次获取位置（观察数据变化）
            if 4 in tests_to_run:
                print("\n--- 测试4：多次获取位置（观察数据变化） ---")
                for i in range(3):
                    positions = hand.get_joint_positions(sync=True, timeout=0.1)
                    if isinstance(positions, (list, tuple)) and len(positions) >= 16:
                        # 显示拇指的4个关节
                        thumb_positions = positions[:4] if len(positions) >= 4 else []
                        thumb_degrees = [math.degrees(p) if p is not None else None for p in thumb_positions]
                        print(f"第{i+1}次获取 - 拇指关节位置（度）: {thumb_degrees}")
                    else:
                        print(f"第{i+1}次获取: {positions}")
                    time.sleep(0.5)
            
            # 测试5：获取指定关节位置（如果支持）
            if 5 in tests_to_run:
                print("\n--- 测试5：获取指定关节位置 ---")
                # 注意：joint_names 参数的使用方式可能需要根据实际实现调整
                # 这里先测试获取所有位置，然后提取特定关节
                all_positions = hand.get_joint_positions(sync=True, timeout=0.1)
                if isinstance(all_positions, (list, tuple)) and len(all_positions) >= 16:
                    # 提取拇指的4个关节（索引0-3）
                    thumb_joints = all_positions[:4]
                    thumb_degrees = [math.degrees(p) if p is not None else None for p in thumb_joints]
                    print(f"拇指的4个关节位置（度）: {thumb_degrees}")
                    
                    # 提取食指的3个关节（索引4-6）
                    index_joints = all_positions[4:7] if len(all_positions) >= 7 else []
                    index_degrees = [math.degrees(p) if p is not None else None for p in index_joints]
                    print(f"食指的3个关节位置（度）: {index_degrees}")
                    
                    # 提取中指的3个关节（索引7-9）
                    middle_joints = all_positions[7:10] if len(all_positions) >= 10 else []
                    middle_degrees = [math.degrees(p) if p is not None else None for p in middle_joints]
                    print(f"中指的3个关节位置（度）: {middle_degrees}")
            
            # 如果测试6需要运行，或者测试3运行了（测试3会改变位置），则执行回零
            # 如果只运行测试6，也需要先回零
            if 6 in tests_to_run or (3 in tests_to_run):
                print("\n执行回零操作...")
                success = hand.hand_zero()
                print(f"回零结果: {'成功' if success else '失败'}")
                time.sleep(1)
            
            # 测试6：回零后获取位置
            if 6 in tests_to_run:
                print("\n--- 测试6：回零后获取位置 ---")
                zero_positions = hand.get_joint_positions(sync=True, timeout=0.1)
                print(f"回零后位置（弧度）: {zero_positions}")
                if isinstance(zero_positions, (list, tuple)) and len(zero_positions) >= 16:
                    zero_degrees = [math.degrees(p) if p is not None else None for p in zero_positions]
                    print(f"回零后位置（度）: {zero_degrees}")
            
            # 测试7：从0位置插补到目标位置，每步获取位置
            if 7 in tests_to_run:
                print("\n--- 测试7：从0位置插补到目标位置，每步获取位置 ---")
                # 目标位置（与测试3相同）
                target_positions = [
                    # 拇指的4个关节
                    0.0, math.radians(10.0), math.radians(20.0), math.radians(15.0),
                    # 食指的3个关节
                    0.0, math.radians(30.0), math.radians(40.0),
                    # 中指的3个关节
                    0.0, math.radians(25.0), math.radians(35.0),
                    # 无名指的3个关节
                    0.0, math.radians(20.0), math.radians(30.0),
                    # 小指的3个关节
                    0.0, math.radians(15.0), math.radians(25.0)
                ]
                
                # 先回零，确保从0位置开始
                # print("先回零，确保从0位置开始...")
                # hand.hand_zero()
                # time.sleep(1)
                
                # 获取初始位置（应该是0或接近0）- 使用异步方式
                print("使用异步方式获取初始位置...")
                initial_positions = hand.get_joint_positions(sync=False)
                print(f"初始位置（弧度）: {initial_positions[:5]}...")
                if isinstance(initial_positions, (list, tuple)) and len(initial_positions) >= 16:
                    initial_degrees = [math.degrees(p) if p is not None else None for p in initial_positions[:5]]
                    print(f"初始位置（度，前5个关节）: {initial_degrees}")
                
                # 插补参数
                interpolation_steps = 100  # 插补步数
                step_delay = 0.0  # 每步延迟时间（秒）
                
                print(f"\n开始插补：从0位置到目标位置，共{interpolation_steps}步，每步延迟{step_delay}秒")
                print(f"目标位置（度，前5个关节）: {[math.degrees(p) if p is not None else None for p in target_positions[:5]]}")
                
                # 执行插补
                for step in range(interpolation_steps + 1):
                    # 计算插补系数 t ∈ [0, 1]
                    t = step / interpolation_steps
                    
                    # 计算当前步的插补位置
                    interpolated_positions = []
                    for i in range(len(target_positions)):
                        if i < len(initial_positions) and initial_positions[i] is not None:
                            start_pos = initial_positions[i]
                            end_pos = target_positions[i]
                            interpolated_pos = start_pos + (end_pos - start_pos) * t
                            interpolated_positions.append(interpolated_pos)
                        else:
                            interpolated_positions.append(target_positions[i] * t)
                    
                    # 设置插补位置
                    success = hand.move_joints_pos(interpolated_positions, speed=0.8, use_broadcast=True)
                    if not success:
                        print(f"警告：第{step}步设置位置失败")
                    
                    # 获取实际位置（使用异步方式）
                    actual_positions = hand.get_joint_positions(sync=False)
                    
                    # # 显示进度和位置信息
                    # if isinstance(actual_positions, (list, tuple)) and len(actual_positions) >= 16:
                    #     # 显示前5个关节的位置对比
                    #     print(f"\n步骤 {step}/{interpolation_steps} (进度: {t*100:.1f}%):")
                    #     print(f"  目标位置（度，前5个关节）: {[math.degrees(p) if p is not None else None for p in interpolated_positions[:5]]}")
                    #     actual_degrees = [math.degrees(p) if p is not None else None for p in actual_positions[:5]]
                    #     print(f"  实际位置（度，前5个关节）: {actual_degrees}")
                        
                    #     # 计算误差
                    #     errors = []
                    #     for i in range(min(5, len(interpolated_positions), len(actual_positions))):
                    #         if interpolated_positions[i] is not None and actual_positions[i] is not None:
                    #             error = abs(interpolated_positions[i] - actual_positions[i])
                    #             errors.append(math.degrees(error))
                    #         else:
                    #             errors.append(None)
                    #     print(f"  位置误差（度，前5个关节）: {errors}")
                    # else:
                    #     print(f"步骤 {step}/{interpolation_steps}: 获取位置失败或数据格式错误")
                    
                    # 等待一段时间，让电机运动
                    # if step < interpolation_steps:  # 最后一步不需要延迟
                    #     time.sleep(step_delay)
                
                print("\n插补完成！")
                
                # 最后再次获取位置，确认是否到达目标（使用异步方式）
                print("使用异步方式获取最终位置...")
                final_positions = hand.get_joint_positions(sync=False)
                if isinstance(final_positions, (list, tuple)) and len(final_positions) >= 16:
                    final_degrees = [math.degrees(p) if p is not None else None for p in final_positions[:5]]
                    target_degrees = [math.degrees(p) if p is not None else None for p in target_positions[:5]]
                    print(f"\n最终位置（度，前5个关节）: {final_degrees}")
                    print(f"目标位置（度，前5个关节）: {target_degrees}")
                    
                    # 计算最终误差
                    final_errors = []
                    for i in range(min(5, len(target_positions), len(final_positions))):
                        if target_positions[i] is not None and final_positions[i] is not None:
                            error = abs(target_positions[i] - final_positions[i])
                            final_errors.append(math.degrees(error))
                        else:
                            final_errors.append(None)
                    print(f"最终误差（度，前5个关节）: {final_errors}")
                
                time.sleep(1)
                
                # hand.hand_zero()
                # time.sleep(1)
            
        else:
            print(f"GaiaHand20 连接失败 (串口: {ports_config['right']})")
            
    except Exception as e:
        print(f"GaiaHand20 get_joint_positions 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if hand and hand.is_connected():
            print("回零...")
            hand.hand_zero()
            time.sleep(1)
            print("下使能所有关节...")
            disable_success = hand.enable_all_motors_broadcast(False)
            print(f"下使能结果: {'成功' if disable_success else '失败'}")
            hand.close()


def test_gaia20_hand_get_joints_pos_vel(ports_config, tests_to_run=None):
    """
    测试 GaiaHand20Adapter.get_joints_pos_vel：关节位置(rad)与角速度(rad/s)，协议字典键与 move_joints_pos 一致。

    单手右手：键 ``3`` 为整手位置、``5`` 为整手速度；双手另含 ``4``/``6``（左手）。
    无参调用返回整手；传入 ``FingerType`` + ``JointType`` 时仅返回该关节（单元素列表）。

    连接方式可与 ``test_gaia20_hand_get_joint_positions`` 对齐（串口 / SLCAN、波特率、主控板）。

    Args:
        ports_config: 串口配置字典
        tests_to_run: 子测试列表。默认 ``[7]``（与 ``test_gaia20_hand_get_joint_positions`` 测试7 同级：插补过程边运动边读）。
                     1 — 无参整手读取；2 — 指定拇指第一关节；3 — 运动后再次整手读取对比拇指；
                     7 — 从当前位置插补到目标位置，每步 ``get_joints_pos_vel`` 读取整手位置(3)与速度(5)。
    """
    print("\n=== 测试 GaiaHand20 get_joints_pos_vel（位置+速度，协议字典 3/5）===")

    if tests_to_run is None:
        tests_to_run = [7]
    elif not tests_to_run:
        tests_to_run = [1, 2, 3, 7]

    print(f"将要运行的测试: {tests_to_run}")

    if not ports_config or not ports_config['right']:
        print("未找到可用的右手串口，跳过 get_joints_pos_vel 测试")
        return

    hand = None
    try:
        # 与 test_gaia20_hand_get_joint_positions 相同，可按硬件改为一组实际配置：
        # hand = create_hand("gaia20", "right", port=ports_config['right'], baudrate=921600, has_main_board=True)
        # hand = create_hand("gaia20", "right", port=ports_config['right'], baudrate=230400)
        # hand = create_hand("gaia20", "right", port='COM6', use_slcan=True, has_main_board=True)
        # hand = create_hand("gaia20", "right", port=ports_config['right'], baudrate=230400)

        hand = create_hand("gaia20", "right", port='COM6', use_slcan=True, has_main_board=True)

        if not hasattr(hand, 'get_joints_pos_vel'):
            print("当前适配器未实现 get_joints_pos_vel，跳过")
            return

        if hand.connect():
            print(f"GaiaHand20 连接成功 (串口: {ports_config['right']})")

            set_motor_smooth_level(hand, device_id=255, level=3, description="get_joints_pos_vel 测试")

            print("上使能所有关节...")
            enable_success = hand.enable_all_motors_broadcast(True)
            print(f"上使能结果: {'成功' if enable_success else '失败'}")
            if not enable_success:
                print("上使能失败，无法继续测试")
                return

            time.sleep(0.5)

            if 1 in tests_to_run:
                print("\n--- 测试1：无参整手 get_joints_pos_vel() ---")
                full = hand.get_joints_pos_vel()
                print(f"返回顶层键: {sorted(full.keys())}")
                for top_key in sorted(full.keys()):
                    side = {3: "右手位置(rad)", 4: "左手位置(rad)", 5: "右手速度(rad/s)", 6: "左手速度(rad/s)"}.get(
                        top_key, f"键{top_key}"
                    )
                    inner = full[top_key]
                    print(f"  [{top_key}] {side}，手指编号: {sorted(inner.keys())}")
                    if 1 in inner:
                        pos_thumb = inner[1]
                        deg = [math.degrees(v) if v is not None else None for v in pos_thumb]
                        print(f"      拇指各关节（本组数值）: {pos_thumb}")
                        if top_key in (3, 4):
                            print(f"      拇指各关节（度）: {deg}")

            if 2 in tests_to_run:
                # print("\n--- 测试2：指定拇指第一关节 FingerType.THUMB, JointType.JOINT_1 ---")
                # one = hand.get_joints_pos_vel(FingerType.THUMB, JointType.JOINT_1, timeout=0.2)
                # print(f"返回: {one}")
                # for k in sorted(one.keys()):
                #     label = "位置(rad)" if k in (3, 4) else "速度(rad/s)"
                #     print(f"  [{k}] {label}: {one[k]}")
                pass

            if 3 in tests_to_run:
                # print("\n--- 测试3：小幅动指后再次整手读取（观察拇指位置/速度变化） ---")
                # before = hand.get_joints_pos_vel()
                # bump = [
                #     0.0,
                #     math.radians(12.0),
                #     math.radians(10.0),
                #     math.radians(8.0),
                #     0.0,
                #     math.radians(5.0),
                #     math.radians(5.0),
                #     0.0,
                #     math.radians(5.0),
                #     math.radians(5.0),
                #     0.0,
                #     math.radians(5.0),
                #     math.radians(5.0),
                #     0.0,
                #     math.radians(5.0),
                #     math.radians(5.0),
                # ]
                # hand.move_joints_pos(bump, speed=0.5, use_broadcast=True)
                # time.sleep(1.0)
                # after = hand.get_joints_pos_vel()
                # if 3 in before and 3 in after and 1 in before[3] and 1 in after[3]:
                #     print(f"拇指位置(rad) 运动前: {before[3][1]}")
                #     print(f"拇指位置(rad) 运动后: {after[3][1]}")
                # if 5 in before and 5 in after and 1 in before[5] and 1 in after[5]:
                #     print(f"拇指速度(rad/s) 运动前: {before[5][1]}")
                #     print(f"拇指速度(rad/s) 运动后: {after[5][1]}")
                pass

            if 7 in tests_to_run:
                print(
                    "\n--- 测试7：插补运动，每步 get_joints_pos_vel（边运动边读角度与角速度，对齐 get_joint_positions 测试7）---"
                )
                target_positions = [
                    0.0,
                    math.radians(10.0),
                    math.radians(20.0),
                    math.radians(15.0),
                    0.0,
                    math.radians(30.0),
                    math.radians(40.0),
                    0.0,
                    math.radians(25.0),
                    math.radians(35.0),
                    0.0,
                    math.radians(20.0),
                    math.radians(30.0),
                    0.0,
                    math.radians(15.0),
                    math.radians(25.0),
                ]
                print("使用异步方式获取初始位置（与插补起点一致）...")
                initial_positions = hand.get_joint_positions(sync=False)
                print(f"初始位置（弧度，前5关节）: {initial_positions[:5] if isinstance(initial_positions, (list, tuple)) else initial_positions}...")
                if isinstance(initial_positions, (list, tuple)) and len(initial_positions) >= 16:
                    print(
                        f"初始位置（度，前5关节）: {[math.degrees(p) if p is not None else None for p in initial_positions[:5]]}"
                    )

                interpolation_steps = 10
                step_delay = 0.0
                print(
                    f"\n开始插补：当前位置 → 目标位置，共 {interpolation_steps} 步，每步后读 get_joints_pos_vel，步间延迟 {step_delay}s"
                )
                print(
                    f"目标位置（度，前5关节）: {[math.degrees(p) if p is not None else None for p in target_positions[:5]]}"
                )

                for step in range(interpolation_steps + 1):
                    t = step / interpolation_steps
                    interpolated_positions = []
                    for i in range(len(target_positions)):
                        if (
                            isinstance(initial_positions, (list, tuple))
                            and i < len(initial_positions)
                            and initial_positions[i] is not None
                        ):
                            start_pos = initial_positions[i]
                            end_pos = target_positions[i]
                            interpolated_positions.append(start_pos + (end_pos - start_pos) * t)
                        else:
                            interpolated_positions.append(target_positions[i] * t)

                    success = hand.move_joints_pos(interpolated_positions, speed=0.8, use_broadcast=True)
                    if not success:
                        print(f"警告：第 {step} 步设置位置失败")

                    pv = hand.get_joints_pos_vel(timeout=0.025)
                    if step % 10 == 0 or step == interpolation_steps:
                        print(f"\n步骤 {step}/{interpolation_steps} (进度 {t * 100:.1f}%):")
                        if 3 in pv and 1 in pv[3]:
                            pos_deg = [math.degrees(x) if x is not None else None for x in pv[3][1]]
                            print(f"  拇指位置（度，协议键3）: {pos_deg}")
                        if 5 in pv and 1 in pv[5]:
                            vel_dps = [math.degrees(w) if w is not None else None for w in pv[5][1]]
                            print(f"  拇指角速度（°/s，协议键5，由 rad/s 换算）: {vel_dps}")

                print("\n插补完成。最终整手 get_joints_pos_vel：")
                final_pv = hand.get_joints_pos_vel(timeout=0.1)
                if 3 in final_pv and 5 in final_pv and 1 in final_pv[3]:
                    fd = [math.degrees(x) if x is not None else None for x in final_pv[3][1]]
                    td = [math.degrees(p) if p is not None else None for p in target_positions[:4]]
                    print(f"  拇指最终位置（度）: {fd}")
                    print(f"  拇指目标位置（度）: {td}")
                time.sleep(1)

        else:
            print(f"GaiaHand20 连接失败 (串口: {ports_config['right']})")

    except Exception as e:
        print(f"GaiaHand20 get_joints_pos_vel 测试失败: {e}")
        import traceback

        traceback.print_exc()
    finally:
        if hand and hand.is_connected():
            print("回零...")
            try:
                hand.hand_zero()
                time.sleep(1)
            except Exception:
                pass
            print("下使能所有关节...")
            disable_success = hand.enable_all_motors_broadcast(False)
            print(f"下使能结果: {'成功' if disable_success else '失败'}")
            hand.close()


def test_gaia20_hand_move_joints_pos_list(ports_config):
    """
    测试 GaiaHand20 的 move_joints_pos 功能（列表格式，16关节版本）
    
    ⭐ 推荐使用：Gaia20当前主要维护版本
    
    波特率配置：
    - 不带主控板版本：230400（此函数使用的配置）
    - 带主控板版本：921600（高性能配置，请使用 test_gaia20_hand_smooth_transition() 查看示例）
    """
    print("\n=== 测试 GaiaHand20 move_joints_pos 功能（列表格式，16关节版本）===")
    
    if not ports_config or not ports_config['right']:
        print("未找到可用的右手串口，跳过单手测试")
        return
    
    hand = None
    try:
        # 创建右手 GaiaHand20 实例
        hand = create_hand("gaia20", "right", port=ports_config['right'], baudrate=230400)

        if hand.connect():
            print(f"GaiaHand20 连接成功 (串口: {ports_config['right']})")
            
            # 设置电机平滑等级（device_id=255表示广播所有电机，level=3）
            # 平滑等级范围：0-5，数值越大平滑效果越好
            set_motor_smooth_level(hand, device_id=255, level=3, description="连接后初始化")
            
            # 等待设置生效
            time.sleep(0.5)
            
            # 上使能所有关节
            print("上使能所有关节...")
            enable_success = hand.enable_all_motors_broadcast(True)
            print(f"上使能结果: {'成功' if enable_success else '失败'}")
            
            if not enable_success:
                print("上使能失败，无法继续测试")
                return
            
            # 等待使能稳定
            time.sleep(1)
            
            # 测试单手模式 - 16个关节位置
            print("\n--- 测试单手模式（16关节） ---")
            
            # 创建16关节位置数据：拇指4关节，其他手指各3关节（弧度制）
            custom_positions_16 = [
                # 拇指的4个关节
                0.0, math.radians(10.0), math.radians(10.0), math.radians(10.0),
                # 食指的3个关节
                0.0, math.radians(10.0), math.radians(10.0),
                # 中指的3个关节
                0.0, math.radians(13.0), math.radians(15.0),
                # 无名指的3个关节
                0.0, math.radians(18.0), math.radians(10.0),
                # 小指的3个关节
                0.0, math.radians(19.0), math.radians(10.0)
            ]
            
            print(f"设置16关节位置数据: {custom_positions_16}")
            success = hand.move_joints_pos(custom_positions_16, speed=1, use_broadcast=True)
            print(f"16关节位置结果: {'成功' if success else '失败'}")
            
            # 等待2秒
            time.sleep(1)
            
            # 测试拇指独立运动（4关节）
            print("\n--- 测试拇指独立运动（4关节） ---")
            
            thumb_positions = [
                # 拇指的4个关节（弧度制）
                math.radians(10.0), math.radians(30.0), math.radians(45.0), math.radians(25.0),
                # 其他手指保持不动
                0.0, 0.0, 0.0,  # 食指
                0.0, 0.0, 0.0,  # 中指
                0.0, 0.0, 0.0,  # 无名指
                0.0, 0.0, 0.0   # 小指
            ]
            
            print("执行拇指弯曲运动...")
            success = hand.move_joints_pos(thumb_positions, speed=0.8, use_broadcast=True)
            print(f"拇指运动结果: {'成功' if success else '失败'}")
            
            time.sleep(1)
            
            # 回零
            print("执行回零操作...")
            success = hand.hand_zero()
            print(f"回零结果: {'成功' if success else '失败'}")
            time.sleep(1)
            
        else:
            print(f"GaiaHand20 连接失败 (串口: {ports_config['right']})")
            
    except Exception as e:
        print(f"GaiaHand20 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if hand and hand.is_connected():
            print("回零...")
            hand.hand_zero()
            time.sleep(1)
            print("下使能所有关节...")
            disable_success = hand.enable_all_motors_broadcast(False)
            print(f"下使能结果: {'成功' if disable_success else '失败'}")
            hand.close()


def test_gaia20_hand_move_joints_pos_dict(ports_config):
    """
    测试 GaiaHand20 的 move_joints_pos 功能（字典格式，16关节版本）
    
    ⭐ 推荐使用：Gaia20当前主要维护版本
    
    波特率配置：230400（不带主控板版本）
    """
    print("\n=== 测试 GaiaHand20 move_joints_pos 功能（字典格式，16关节版本）===")
    
    if not ports_config or not ports_config['right']:
        print("未找到可用的右手串口，跳过字典格式测试")
        return
    
    hand = None
    try:
        # 创建右手 GaiaHand20 实例
        # ⭐ 波特率配置：230400（不带主控板版本）
        # 如果使用带主控板版本，请修改为：baudrate=921600
        hand = create_hand("gaia20", "right", port=ports_config['right'], baudrate=230400)

        if hand.connect():
            print(f"GaiaHand20 连接成功 (串口: {ports_config['right']})")
            
            # 设置电机平滑等级（device_id=255表示广播所有电机，level=3）
            # 平滑等级范围：0-5，数值越大平滑效果越好
            set_motor_smooth_level(hand, device_id=255, level=3, description="连接后初始化")
            
            # 等待设置生效
            time.sleep(0.5)
            
            # 上使能所有关节
            print("上使能所有关节...")
            enable_success = hand.enable_all_motors_broadcast(True)
            print(f"上使能结果: {'成功' if enable_success else '失败'}")
            
            if not enable_success:
                print("上使能失败，无法继续测试")
                return
            
            # 等待使能稳定
            time.sleep(1)
            
            # 测试1：使用字典格式设置右手位置（单手模式）
            print("\n--- 测试1：字典格式设置右手位置（单手模式） ---")
            right_hand_data = {
                1: [0.0, math.radians(10.0), math.radians(10.0), math.radians(10.0)],  # 拇指（4个关节，弧度制）
                2: [0.0, math.radians(10.0), math.radians(10.0)],  # 食指（3个关节，弧度制）
                3: [0.0, math.radians(13.0), math.radians(15.0)],  # 中指（3个关节，弧度制）
                4: [0.0, math.radians(18.0), math.radians(10.0)],  # 无名指（3个关节，弧度制）
                5: [0.0, math.radians(19.0), math.radians(10.0)]   # 小指（3个关节，弧度制）
            }
            
            positions_dict = {1: right_hand_data}  # 1=右手
            print(f"设置右手位置数据（字典格式，弧度制）")
            print(f"  拇指: {right_hand_data[1]}")
            print(f"  食指: {right_hand_data[2]}")
            print(f"  中指: {right_hand_data[3]}")
            print(f"  无名指: {right_hand_data[4]}")
            print(f"  小指: {right_hand_data[5]}")
            
            success = hand.move_joints_pos(positions_dict, speed=1, use_broadcast=True)
            print(f"字典格式设置结果: {'成功' if success else '失败'}")
            
            if success:
                time.sleep(1)
                # 获取当前位置验证
                current_positions = hand.get_joint_positions()
                print(f"当前位置: {current_positions}")
            
            # 测试2：使用字典格式设置拇指弯曲
            print("\n--- 测试2：字典格式设置拇指弯曲 ---")
            thumb_bend_data = {
                1: [math.radians(10.0), math.radians(30.0), math.radians(45.0), math.radians(25.0)],  # 拇指弯曲（4个关节，弧度制）
                2: [0.0, 0.0, 0.0],  # 食指保持不动
                3: [0.0, 0.0, 0.0],  # 中指保持不动
                4: [0.0, 0.0, 0.0],  # 无名指保持不动
                5: [0.0, 0.0, 0.0]   # 小指保持不动
            }
            
            positions_dict = {1: thumb_bend_data}
            print(f"设置拇指弯曲（字典格式，弧度制）")
            success = hand.move_joints_pos(positions_dict, speed=0.8, use_broadcast=True)
            print(f"拇指弯曲设置结果: {'成功' if success else '失败'}")
            
            time.sleep(1)
            
            # 测试3：使用字典格式回零（所有关节伸直）
            print("\n--- 测试3：字典格式回零（所有关节伸直） ---")
            zero_data = {
                1: [0.0, 0.0, 0.0, 0.0],  # 拇指（4个关节）
                2: [0.0, 0.0, 0.0],  # 食指（3个关节）
                3: [0.0, 0.0, 0.0],  # 中指（3个关节）
                4: [0.0, 0.0, 0.0],  # 无名指（3个关节）
                5: [0.0, 0.0, 0.0]   # 小指（3个关节）
            }
            
            positions_dict = {1: zero_data}
            print("执行回零操作（字典格式）...")
            success = hand.move_joints_pos(positions_dict, speed=1, use_broadcast=True)
            print(f"回零结果: {'成功' if success else '失败'}")
            
            time.sleep(1)
            
            # 测试4：指令6格式测试（单个关节控制）
            print("\n--- 测试4：指令6格式测试（单个关节控制） ---")
            # 指令6格式：6: [手部, 手指, 关节, 位置值(弧度)]
            # 右手，拇指，第2个关节，30度（弧度制）
            command_6_data = [1, 1, 2, math.radians(30.0)]
            positions_dict = {6: command_6_data}
            
            print(f"指令6数据: 右手(1), 拇指(1), 关节2, 角度{math.degrees(math.radians(30.0)):.1f}度")
            success = hand.move_joints_pos(positions_dict, speed=0.8, use_broadcast=False)
            print(f"指令6设置结果: {'成功' if success else '失败'}")
            
            time.sleep(1)

            # 回零
            print("执行回零操作...")
            success = hand.hand_zero()
            print(f"回零结果: {'成功' if success else '失败'}")
            time.sleep(1)
            
        else:
            print(f"GaiaHand20 连接失败 (串口: {ports_config['right']})")
            
    except Exception as e:
        print(f"GaiaHand20 字典格式测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if hand and hand.is_connected():
            print("回零...")
            hand.hand_zero()
            time.sleep(1)
            print("下使能所有关节...")
            disable_success = hand.enable_all_motors_broadcast(False)
            print(f"下使能结果: {'成功' if disable_success else '失败'}")
            hand.close()


def test_gaia20_hand_double_move_joints_pos_dict(ports_config):
    """
    测试 GaiaHand20 双手模式的 move_joints_pos 功能（字典格式，32关节）
    
    ⭐ 推荐使用：Gaia20当前主要维护版本
    
    波特率配置：230400（不带主控板版本）
    """
    print("\n=== 测试 GaiaHand20 双手模式 move_joints_pos 功能（字典格式，32关节）===")
    
    if not ports_config or not ports_config['left'] or not ports_config['right']:
        print("未找到可用的左右手串口，跳过双手字典格式测试")
        return
    
    hand = None
    try:
        # 创建双手 GaiaHand20 实例
        # ⭐ 波特率配置：230400（不带主控板版本，默认配置）
        # 如果使用带主控板版本，需要在create_hand中添加baudrate=921600参数
        hand = create_hand("gaia20", "double", left_port=ports_config['left'], right_port=ports_config['right'])
        
        if hand.connect():
            print(f"GaiaHand20 双手模式连接成功 (左手: {ports_config['left']}, 右手: {ports_config['right']})")
            
            # 设置电机平滑等级（device_id=255表示广播所有电机，level=3）
            # 平滑等级范围：0-5，数值越大平滑效果越好
            set_motor_smooth_level(hand, device_id=255, level=3, description="连接后初始化")
            
            # 等待设置生效
            time.sleep(0.5)
            
            # 上使能所有关节
            print("上使能所有关节...")
            enable_success = hand.enable_all_motors_broadcast(True)
            print(f"上使能结果: {'成功' if enable_success else '失败'}")
            
            if not enable_success:
                print("上使能失败，无法继续测试")
                return
            
            # 等待使能稳定
            time.sleep(1)
            
            # 测试1：使用字典格式设置双手位置
            print("\n--- 测试1：字典格式设置双手位置 ---")
            right_hand_data = {
                1: [0.0, math.radians(20.0), math.radians(30.0), math.radians(15.0)],  # 拇指（4个关节，弧度制）
                2: [0.0, math.radians(40.0), math.radians(55.0)],  # 食指（3个关节，弧度制）
                3: [0.0, math.radians(35.0), math.radians(45.0)],  # 中指（3个关节，弧度制）
                4: [0.0, math.radians(30.0), math.radians(40.0)],  # 无名指（3个关节，弧度制）
                5: [0.0, math.radians(25.0), math.radians(35.0)]   # 小指（3个关节，弧度制）
            }
            
            left_hand_data = {
                1: [0.0, math.radians(20.0), math.radians(30.0), math.radians(15.0)],  # 拇指（4个关节，弧度制）
                2: [0.0, math.radians(40.0), math.radians(55.0)],  # 食指（3个关节，弧度制）
                3: [0.0, math.radians(35.0), math.radians(45.0)],  # 中指（3个关节，弧度制）
                4: [0.0, math.radians(30.0), math.radians(40.0)],  # 无名指（3个关节，弧度制）
                5: [0.0, math.radians(25.0), math.radians(35.0)]   # 小指（3个关节，弧度制）
            }
            
            positions_dict = {
                1: right_hand_data,  # 1=右手
                2: left_hand_data    # 2=左手
            }
            
            print(f"设置双手位置数据（字典格式，弧度制）")
            print(f"  右手拇指: {right_hand_data[1]}")
            print(f"  左手拇指: {left_hand_data[1]}")
            
            success = hand.move_joints_pos(positions_dict, speed=0.5, use_broadcast=True)
            print(f"双手字典格式设置结果: {'成功' if success else '失败'}")
            
            time.sleep(2)
            
            # 测试2：使用字典格式设置不同手势
            print("\n--- 测试2：字典格式设置不同手势 ---")
            # 右手：拇指弯曲
            right_custom = {
                1: [math.radians(5.0), math.radians(25.0), math.radians(40.0), math.radians(20.0)],  # 拇指弯曲（4个关节，弧度制）
                2: [0.0, 0.0, 0.0],  # 食指保持不动
                3: [0.0, 0.0, 0.0],  # 中指保持不动
                4: [0.0, 0.0, 0.0],  # 无名指保持不动
                5: [0.0, 0.0, 0.0]   # 小指保持不动
            }
            
            # 左手：食指弯曲
            left_custom = {
                1: [0.0, 0.0, 0.0, 0.0],  # 拇指保持不动
                2: [0.0, math.radians(45.0), math.radians(60.0)],  # 食指弯曲（3个关节，弧度制）
                3: [0.0, 0.0, 0.0],  # 中指保持不动
                4: [0.0, 0.0, 0.0],  # 无名指保持不动
                5: [0.0, 0.0, 0.0]   # 小指保持不动
            }
            
            positions_dict = {
                1: right_custom,  # 右手
                2: left_custom     # 左手
            }
            
            print(f"设置自定义双手位置: 右手拇指弯曲，左手食指弯曲（字典格式，弧度制）")
            success = hand.move_joints_pos(positions_dict, speed=0.5, use_broadcast=True)
            print(f"自定义双手位置结果: {'成功' if success else '失败'}")
            
            time.sleep(2)
            
            # 测试3：使用字典格式回零（双手张开）
            print("\n--- 测试3：字典格式回零（双手张开） ---")
            zero_data = {
                1: [0.0, 0.0, 0.0, 0.0],  # 拇指（4个关节）
                2: [0.0, 0.0, 0.0],  # 食指（3个关节）
                3: [0.0, 0.0, 0.0],  # 中指（3个关节）
                4: [0.0, 0.0, 0.0],  # 无名指（3个关节）
                5: [0.0, 0.0, 0.0]   # 小指（3个关节）
            }
            
            positions_dict = {
                1: zero_data,  # 右手
                2: zero_data   # 左手
            }
            
            print("执行双手回零操作（字典格式）...")
            success = hand.move_joints_pos(positions_dict, speed=0.5, use_broadcast=True)
            print(f"双手回零结果: {'成功' if success else '失败'}")
            
            time.sleep(2)
            
        else:
            print(f"GaiaHand20 双手模式连接失败 (左手: {ports_config['left']}, 右手: {ports_config['right']})")
            
    except Exception as e:
        print(f"GaiaHand20 双手模式字典格式测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if hand and hand.is_connected():
            print("回零...")
            hand.hand_zero()
            time.sleep(1)
            print("下使能所有关节...")
            disable_success = hand.enable_all_motors_broadcast(False)
            print(f"下使能结果: {'成功' if disable_success else '失败'}")
            hand.close()


def test_gaia20_hand_smooth_transition(ports_config):
    """
    测试 GaiaHand20 平滑过渡功能（16关节版本）
    
    ⭐ 推荐使用：Gaia20当前主要维护版本
    
    波特率配置：921600（带主控板版本，高性能配置）
    """
    print("\n=== 测试 GaiaHand20 平滑过渡功能（16关节版本）===")
    
    if not ports_config or not ports_config['right']:
        print("未找到可用的右手串口，跳过平滑过渡测试")
        return
    
    hand = None
    try:
        # 创建右手 GaiaHand20 实例
        # ⭐ 波特率配置：921600（带主控板版本，高性能配置）
        # 如果使用不带主控板版本，请修改为：baudrate=230400
        hand = create_hand("gaia20", "right", port=ports_config['right'], baudrate=921600)
        
        if hand.connect():
            print(f"GaiaHand20 连接成功，开始平滑过渡测试 (串口: {ports_config['right']})")
            
            # 设置电机平滑等级（device_id=255表示广播所有电机，level=3）
            # 平滑等级范围：0-5，数值越大平滑效果越好
            set_motor_smooth_level(hand, device_id=255, level=3, description="连接后初始化")
            
            # 等待设置生效
            time.sleep(0.5)
            
            # 上使能所有关节
            print("上使能所有关节...")
            enable_success = hand.enable_all_motors_broadcast(True)
            print(f"上使能结果: {'成功' if enable_success else '失败'}")
            
            if not enable_success:
                print("上使能失败，无法继续测试")
                return
            
            # 等待使能稳定
            time.sleep(1)
            
            # 创建起始和结束位置（弧度制）
            start_positions_16 = [0.0] * 16
            end_positions_16 = [
                # 拇指的4个关节
                0.0, math.radians(20.0), math.radians(35.0), math.radians(18.0),
                # 食指的3个关节
                0.0, math.radians(43.0), math.radians(56.0),
                # 中指的3个关节
                0.0, math.radians(33.0), math.radians(25.0),
                # 无名指的3个关节
                0.0, math.radians(28.0), math.radians(18.0),
                # 小指的3个关节
                0.0, math.radians(19.0), math.radians(26.0)
            ]
            
            print("执行平滑过渡：从伸直状态到弯曲状态")
            
            # 分8步过渡
            for i in range(9):
                t = i / 8.0
                positions = []
                for j in range(16):
                    pos = start_positions_16[j] + (end_positions_16[j] - start_positions_16[j]) * t
                    positions.append(pos)
                
                print(f"步骤 {i+1}/9: 过渡进度 {t*100:.1f}%")
                hand.move_joints_pos(positions, speed=0.5, use_broadcast=True)
                time.sleep(0.1)
                current_positions = hand.get_joint_positions()
                print(f"当前关节位置: {current_positions}")

            print("平滑过渡完成")
            
            time.sleep(2)
            
            # 反向过渡：从弯曲状态到伸直状态
            print("执行反向过渡：从弯曲状态到伸直状态")
            
            for i in range(10):
                t = i / 10.0
                positions = []
                for j in range(16):
                    pos = end_positions_16[j] + (start_positions_16[j] - end_positions_16[j]) * t
                    positions.append(pos)
                
                print(f"步骤 {i+1}/10: 过渡进度 {t*100:.1f}%")
                hand.move_joints_pos(positions, speed=0.5, use_broadcast=True)
                time.sleep(0.1)
                current_positions = hand.get_joint_positions()
                print(f"当前关节位置: {current_positions}")
            
            print("反向过渡完成")

            time.sleep(2)
            
        else:
            print(f"GaiaHand20 连接失败 (串口: {ports_config['right']})")
            
    except Exception as e:
        print(f"GaiaHand20 平滑过渡测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if hand and hand.is_connected():
            print("回零...")
            hand.hand_zero()
            time.sleep(1)
            print("下使能所有关节...")
            disable_success = hand.enable_all_motors_broadcast(False)
            print(f"下使能结果: {'成功' if disable_success else '失败'}")
            hand.close()


def test_gaia20_hand_double_move_joints_pos(ports_config):
    """
    测试 GaiaHand20 双手模式的 move_joints_pos 功能（32关节）
    
    ⭐ 推荐使用：Gaia20当前主要维护版本
    
    波特率配置：230400（不带主控板版本）
    """
    print("\n=== 测试 GaiaHand20 双手模式 move_joints_pos 功能（32关节）===")
    
    if not ports_config or not ports_config['left'] or not ports_config['right']:
        print("未找到可用的左右手串口，跳过双手测试")
        return
    
    hand = None
    try:
        # 创建双手 GaiaHand20 实例
        # ⭐ 波特率配置：230400（不带主控板版本，默认配置）
        # 如果使用带主控板版本，需要在create_hand中添加baudrate=921600参数
        hand = create_hand("gaia20", "double", left_port=ports_config['left'], right_port=ports_config['right'])
        
        if hand.connect():
            print(f"GaiaHand20 双手模式连接成功 (左手: {ports_config['left']}, 右手: {ports_config['right']})")
            
            # 设置电机平滑等级（device_id=255表示广播所有电机，level=3）
            # 平滑等级范围：0-5，数值越大平滑效果越好
            set_motor_smooth_level(hand, device_id=255, level=3, description="连接后初始化")
            
            # 等待设置生效
            time.sleep(0.5)
            
            # 上使能所有关节
            print("上使能所有关节...")
            enable_success = hand.enable_all_motors_broadcast(True)
            print(f"上使能结果: {'成功' if enable_success else '失败'}")
            
            if not enable_success:
                print("上使能失败，无法继续测试")
                return
            
            # 等待使能稳定
            time.sleep(1)
            
            # 测试双手模式 - 32个关节位置
            print("\n--- 测试双手模式（32关节） ---")
            
            # 创建32关节测试位置数据（弧度制）
            right_positions_16 = [
                # 拇指的4个关节
                0.0, math.radians(20.0), math.radians(30.0), math.radians(15.0),
                # 其他手指
                0.0, math.radians(40.0), math.radians(55.0),  # 食指
                0.0, math.radians(35.0), math.radians(45.0),  # 中指
                0.0, math.radians(30.0), math.radians(40.0),  # 无名指
                0.0, math.radians(25.0), math.radians(35.0)   # 小指
            ]
            left_positions_16 = [
                # 拇指的4个关节
                0.0, math.radians(20.0), math.radians(30.0), math.radians(15.0),
                # 其他手指
                0.0, math.radians(40.0), math.radians(55.0),  # 食指
                0.0, math.radians(35.0), math.radians(45.0),  # 中指
                0.0, math.radians(30.0), math.radians(40.0),  # 无名指
                0.0, math.radians(25.0), math.radians(35.0)   # 小指
            ]
            double_positions_32 = right_positions_16 + left_positions_16
            
            print(f"设置双手32关节位置数据")
            
            # 使用广播模式
            success = hand.move_joints_pos(double_positions_32, speed=0.5, use_broadcast=True)
            print(f"双手32关节广播模式结果: {'成功' if success else '失败'}")
            
            time.sleep(2)
            
            # 测试双手模式 - 自定义位置数据
            print("\n--- 测试双手模式（自定义位置） ---")
            
            # 右手：拇指弯曲（弧度制）
            right_custom = [
                # 拇指的4个关节
                math.radians(5.0), math.radians(25.0), math.radians(40.0), math.radians(20.0),
                # 其他手指
                0.0, 0.0, 0.0,  # 食指
                0.0, 0.0, 0.0,  # 中指
                0.0, 0.0, 0.0,  # 无名指
                0.0, 0.0, 0.0   # 小指
            ]
            
            # 左手：食指弯曲（弧度制）
            left_custom = [
                # 拇指的4个关节
                0.0, 0.0, 0.0, 0.0,
                # 食指
                0.0, math.radians(45.0), math.radians(60.0),
                # 其他手指
                0.0, 0.0, 0.0,  # 中指
                0.0, 0.0, 0.0,  # 无名指
                0.0, 0.0, 0.0   # 小指
            ]
            
            custom_double_positions_32 = right_custom + left_custom
            print(f"设置自定义双手32关节位置: 右手拇指弯曲，左手食指弯曲")
            success = hand.move_joints_pos(custom_double_positions_32, speed=0.5, use_broadcast=True)
            print(f"自定义双手位置结果: {'成功' if success else '失败'}")
            
            time.sleep(2)
            
            # 测试双手模式 - 张开手势
            print("\n--- 测试双手张开手势（32关节） ---")
            double_open_32 = [0.0] * 32
            print("执行双手张开手势...")
            success = hand.move_joints_pos(double_open_32, speed=0.5, use_broadcast=True)
            print(f"双手张开结果: {'成功' if success else '失败'}")
            
            time.sleep(2)
            
        else:
            print(f"GaiaHand20 双手模式连接失败 (左手: {ports_config['left']}, 右手: {ports_config['right']})")
            
    except Exception as e:
        print(f"GaiaHand20 双手模式测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if hand and hand.is_connected():
            print("回零...")
            hand.hand_zero()
            time.sleep(1)
            print("下使能所有关节...")
            disable_success = hand.enable_all_motors_broadcast(False)
            print(f"下使能结果: {'成功' if disable_success else '失败'}")
            hand.close()



def test_gaia20_hand_double_get_joint_positions(ports_config):
    """
    测试 GaiaHand20 双手模式的 get_joint_positions 功能（32关节）
    
    ⭐ 推荐使用：Gaia20当前主要维护版本
    
    波特率配置：230400（不带主控板版本）
    """
    print("\n=== 测试 GaiaHand20 双手模式 get_joint_positions 功能（32关节）===")
    
    if not ports_config or not ports_config['left'] or not ports_config['right']:
        print("未找到可用的左右手串口，跳过双手获取位置测试")
        return
    
    hand = None
    try:
        # 创建双手 GaiaHand20 实例
        # ⭐ 波特率配置：230400（不带主控板版本，默认配置）
        # 如果使用带主控板版本，需要在create_hand中添加baudrate=921600参数
        hand = create_hand("gaia20", "double", left_port=ports_config['left'], right_port=ports_config['right'])
        
        if hand.connect():
            print(f"GaiaHand20 双手模式连接成功 (左手: {ports_config['left']}, 右手: {ports_config['right']})")
            
            # 设置电机平滑等级（device_id=255表示广播所有电机，level=3）
            # 平滑等级范围：0-5，数值越大平滑效果越好
            set_motor_smooth_level(hand, device_id=255, level=3, description="连接后初始化")
            
            # 等待设置生效
            time.sleep(0.5)
            
            # 上使能所有关节
            print("上使能所有关节...")
            enable_success = hand.enable_all_motors_broadcast(True)
            print(f"上使能结果: {'成功' if enable_success else '失败'}")
            
            if not enable_success:
                print("上使能失败，无法继续测试")
                return
            
            # 等待使能稳定
            time.sleep(1)
            
            # 测试1：获取双手所有关节位置（异步模式）
            print("\n--- 测试1：获取双手所有关节位置（异步模式） ---")
            all_positions = hand.get_joint_positions(sync=False)
            print(f"双手所有关节位置（异步）: {all_positions}")
            print(f"位置数据类型: {type(all_positions)}")
            if isinstance(all_positions, dict):
                print(f"手部数量: {len(all_positions)}")
                for hand_name, positions in all_positions.items():
                    print(f"  {hand_name}手位置: {positions}")
                    if isinstance(positions, (list, tuple)):
                        print(f"  {hand_name}手位置数量: {len(positions)}")
            time.sleep(0.5)
            
            # 测试2：获取双手所有关节位置（同步模式）
            print("\n--- 测试2：获取双手所有关节位置（同步模式） ---")
            all_positions_sync = hand.get_joint_positions(sync=True, timeout=0.1)
            print(f"双手所有关节位置（同步）: {all_positions_sync}")
            print(f"位置数据类型: {type(all_positions_sync)}")
            if isinstance(all_positions_sync, dict):
                for hand_name, positions in all_positions_sync.items():
                    print(f"  {hand_name}手位置: {positions}")
                    if isinstance(positions, (list, tuple)) and len(positions) >= 16:
                        # 转换为度数显示
                        degrees = [math.degrees(p) if p is not None else None for p in positions[:5]]
                        print(f"  {hand_name}手前5个关节位置（度）: {degrees}")
            time.sleep(0.5)
            
            # 测试3：设置双手位置后获取位置验证
            print("\n--- 测试3：设置双手位置后获取位置验证 ---")
            # 设置右手位置
            right_positions = [
                # 拇指的4个关节
                0.0, math.radians(10.0), math.radians(20.0), math.radians(15.0),
                # 其他手指
                0.0, math.radians(30.0), math.radians(40.0),  # 食指
                0.0, math.radians(25.0), math.radians(35.0),  # 中指
                0.0, math.radians(20.0), math.radians(30.0),  # 无名指
                0.0, math.radians(15.0), math.radians(25.0)   # 小指
            ]
            # 设置左手位置
            left_positions = [
                # 拇指的4个关节
                0.0, math.radians(5.0), math.radians(15.0), math.radians(10.0),
                # 其他手指
                0.0, math.radians(25.0), math.radians(35.0),  # 食指
                0.0, math.radians(20.0), math.radians(30.0),  # 中指
                0.0, math.radians(15.0), math.radians(25.0),  # 无名指
                0.0, math.radians(10.0), math.radians(20.0)   # 小指
            ]
            
            double_positions = right_positions + left_positions
            print(f"设置双手目标位置（右手前5个关节，弧度）: {right_positions[:5]}")
            print(f"设置双手目标位置（左手前5个关节，弧度）: {left_positions[:5]}")
            success = hand.move_joints_pos(double_positions, speed=0.8, use_broadcast=True)
            print(f"设置双手位置结果: {'成功' if success else '失败'}")
            
            # 等待运动完成
            time.sleep(2)
            
            # 获取当前位置
            current_positions = hand.get_joint_positions(sync=True, timeout=0.1)
            print(f"当前位置: {current_positions}")
            if isinstance(current_positions, dict):
                if 'right' in current_positions:
                    right_current = current_positions['right']
                    if isinstance(right_current, (list, tuple)) and len(right_current) >= 5:
                        print("右手位置对比（前5个关节）:")
                        for i in range(5):
                            target = right_positions[i] if i < len(right_positions) else None
                            current = right_current[i] if i < len(right_current) else None
                            if target is not None and current is not None:
                                diff = abs(target - current)
                                print(f"  关节{i+1}: 目标={math.degrees(target):.2f}°, 当前={math.degrees(current):.2f}°, 误差={math.degrees(diff):.2f}°")
                
                if 'left' in current_positions:
                    left_current = current_positions['left']
                    if isinstance(left_current, (list, tuple)) and len(left_current) >= 5:
                        print("左手位置对比（前5个关节）:")
                        for i in range(5):
                            target = left_positions[i] if i < len(left_positions) else None
                            current = left_current[i] if i < len(left_current) else None
                            if target is not None and current is not None:
                                diff = abs(target - current)
                                print(f"  关节{i+1}: 目标={math.degrees(target):.2f}°, 当前={math.degrees(current):.2f}°, 误差={math.degrees(diff):.2f}°")
            time.sleep(1)
            
            # 测试4：多次获取双手位置（观察数据变化）
            print("\n--- 测试4：多次获取双手位置（观察数据变化） ---")
            for i in range(3):
                positions = hand.get_joint_positions(sync=True, timeout=0.1)
                if isinstance(positions, dict):
                    if 'right' in positions:
                        right_pos = positions['right']
                        if isinstance(right_pos, (list, tuple)) and len(right_pos) >= 4:
                            thumb_degrees = [math.degrees(p) if p is not None else None for p in right_pos[:4]]
                            print(f"第{i+1}次获取 - 右手拇指关节位置（度）: {thumb_degrees}")
                    if 'left' in positions:
                        left_pos = positions['left']
                        if isinstance(left_pos, (list, tuple)) and len(left_pos) >= 4:
                            thumb_degrees = [math.degrees(p) if p is not None else None for p in left_pos[:4]]
                            print(f"第{i+1}次获取 - 左手拇指关节位置（度）: {thumb_degrees}")
                time.sleep(0.5)
            
            # 回零
            print("\n执行双手回零操作...")
            success = hand.hand_zero()
            print(f"回零结果: {'成功' if success else '失败'}")
            time.sleep(1)
            
            # 测试5：回零后获取双手位置
            print("\n--- 测试5：回零后获取双手位置 ---")
            zero_positions = hand.get_joint_positions(sync=True, timeout=0.1)
            print(f"回零后位置: {zero_positions}")
            if isinstance(zero_positions, dict):
                for hand_name, positions in zero_positions.items():
                    if isinstance(positions, (list, tuple)) and len(positions) >= 16:
                        degrees = [math.degrees(p) if p is not None else None for p in positions]
                        print(f"{hand_name}手回零后位置（度）: {degrees}")
            
        else:
            print(f"GaiaHand20 双手模式连接失败 (左手: {ports_config['left']}, 右手: {ports_config['right']})")
            
    except Exception as e:
        print(f"GaiaHand20 双手模式 get_joint_positions 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if hand and hand.is_connected():
            print("回零...")
            hand.hand_zero()
            time.sleep(1)
            print("下使能所有关节...")
            disable_success = hand.enable_all_motors_broadcast(False)
            print(f"下使能结果: {'成功' if disable_success else '失败'}")
            hand.close()


def test_gaia20_hand_reset_zero(ports_config):
    """
    测试 GaiaHand20 手部回零功能（16关节版本）
    
    ⭐ 推荐使用：Gaia20当前主要维护版本
    
    波特率配置：921600（带主控板版本，高性能配置）
    """
    print("\n=== 测试 GaiaHand20 手部回零功能（16关节版本）===")
    
    if not ports_config or not ports_config['right']:
        print("未找到可用的右手串口，跳过回零测试")
        return
    
    hand = None
    try:
        # 创建右手 GaiaHand20 实例
        # ⭐ 波特率配置：921600（带主控板版本，高性能配置）
        # 如果使用不带主控板版本，请修改为：baudrate=230400
        hand = create_hand("gaia20", "right", port=ports_config['right'], baudrate=921600)
        
        if hand.connect():
            print(f"GaiaHand20 连接成功，开始回零测试 (串口: {ports_config['right']})")
            
            # 设置电机平滑等级（device_id=255表示广播所有电机，level=3）
            # 平滑等级范围：0-5，数值越大平滑效果越好
            set_motor_smooth_level(hand, device_id=255, level=3, description="连接后初始化")
            
            # 等待设置生效
            time.sleep(0.5)
            
            # 上使能所有关节
            print("上使能所有关节...")
            enable_success = hand.enable_all_motors_broadcast(True)
            print(f"上使能结果: {'成功' if enable_success else '失败'}")
            
            if not enable_success:
                print("上使能失败，无法继续测试")
                return
            
            # 等待使能稳定
            time.sleep(2)
            
            # 执行回零操作
            print("执行回零操作...")
            hand.hand_zero()
            print("回零操作完成")
            
            time.sleep(2)
            
        else:
            print(f"GaiaHand20 连接失败 (串口: {ports_config['right']})")
            
    except Exception as e:
        print(f"GaiaHand20 回零测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if hand and hand.is_connected():
            print("回零...")
            hand.hand_zero()
            time.sleep(1)
            print("下使能所有关节...")
            disable_success = hand.enable_all_motors_broadcast(False)
            print(f"下使能结果: {'成功' if disable_success else '失败'}")
            hand.close()

def test_gaia_hand_move_joints_pos(ports_config):
    """
    测试 GaiaHand 的 move_joints_pos 功能
    
    ⚠️ 注意：Gaia15已暂停维护，此函数仅用于兼容旧代码
    推荐使用 test_gaia20_hand_move_joints_pos() 函数
    
    波特率配置：
    - 标准配置：230400
    - 注意：此函数中使用了921600，但标准配置应为230400
    """
    print("=== 测试 GaiaHand move_joints_pos 功能 ===")
    
    if not ports_config or not ports_config['right']:
        print("未找到可用的右手串口，跳过单手测试")
        return
    
    hand = None
    try:
        # 创建右手 GaiaHand 实例
        # ⚠️ 注意：Gaia15标准配置应为230400，此处使用921600仅用于示例
        # 建议修改为：baudrate=230400
        hand = create_hand("gaia", "right", port=ports_config['right'], baudrate=921600)

        if hand.connect():
            print(f"GaiaHand 连接成功 (串口: {ports_config['right']})")
            
            # 设置电机平滑等级（device_id=255表示广播所有电机，level=3）
            # 平滑等级范围：0-5，数值越大平滑效果越好
            set_motor_smooth_level(hand, device_id=255, level=3, description="连接后初始化")
            
            # 等待设置生效
            time.sleep(0.5)
            
            # 上使能所有关节
            print("上使能所有关节...")
            enable_success = hand.enable_all_motors_broadcast(True)
            print(f"上使能结果: {'成功' if enable_success else '失败'}")
            
            if not enable_success:
                print("上使能失败，无法继续测试")
                return
            
            # 等待使能稳定
            time.sleep(2)
            
            # 测试单手模式 - 15个关节位置（非广播模式，默认）
            print("\n--- 测试单手模式（非广播） ---")
            
            # 测试单手模式 - 自定义位置数据
            print("\n--- 测试单手模式（自定义位置） ---")
            
            # 创建自定义位置数据：每个手指不同的角度（弧度制）
            custom_positions = [
                # 拇指的3个关节
                0.0, math.radians(27.0), math.radians(43.0),
                # 食指的3个关节
                0.0, math.radians(43.0), math.radians(56.0),
                # 中指的3个关节
                0.0, math.radians(33.0), math.radians(25.0),
                # 无名指的3个关节
                0.0, math.radians(28.0), math.radians(18.0),
                # 小指的3个关节
                0.0, math.radians(19.0), math.radians(26.0)
            ]
            
            print(f"设置自定义位置数据: {custom_positions}")
            success = hand.move_joints_pos(custom_positions, speed=1, use_broadcast=True)
            print(f"自定义位置结果: {'成功' if success else '失败'}")
            
            # 等待2秒
            time.sleep(2)
            
            # 测试单手模式 - 手势执行
            print("\n--- 测试单手模式（手势执行） ---")
            
            # 张开手势（所有关节伸直）
            open_positions = [0.0] * 15
            print("执行张开手势...")
            success = hand.move_joints_pos(open_positions, speed=1, use_broadcast=True)
            print(f"张开结果: {'成功' if success else '失败'}")
            
            time.sleep(2)
            
        else:
            print(f"GaiaHand 连接失败 (串口: {ports_config['right']})")
            
    except Exception as e:
        print(f"GaiaHand 测试失败: {e}")
    finally:
        if hand and hand.is_connected():
            print("回零...")
            hand.hand_zero()
            time.sleep(1)
            print("下使能所有关节...")
            disable_success = hand.enable_all_motors_broadcast(False)
            print(f"下使能结果: {'成功' if disable_success else '失败'}")
            hand.close()

def test_gaia_hand_double_move_joints_pos(ports_config):
    """
    测试 GaiaHand 双手模式的 move_joints_pos 功能
    
    ⚠️ 注意：Gaia15已暂停维护，此函数仅用于兼容旧代码
    推荐使用 test_gaia20_hand_double_move_joints_pos() 函数
    
    波特率配置：230400（标准配置）
    """
    print("\n=== 测试 GaiaHand 双手模式 move_joints_pos 功能 ===")
    
    if not ports_config or not ports_config['left'] or not ports_config['right']:
        print("未找到可用的左右手串口，跳过双手测试")
        return
    
    hand = None
    try:
        # 创建双手 GaiaHand 实例
        # ⚠️ 注意：Gaia15已暂停维护，此函数仅用于兼容旧代码
        # 波特率配置：230400（标准配置）
        hand = create_hand("gaia", "double", left_port=ports_config['left'], right_port=ports_config['right'])
        
        if hand.connect():
            print(f"GaiaHand 双手模式连接成功 (左手: {ports_config['left']}, 右手: {ports_config['right']})")
            
            # 设置电机平滑等级（device_id=255表示广播所有电机，level=3）
            # 平滑等级范围：0-5，数值越大平滑效果越好
            set_motor_smooth_level(hand, device_id=255, level=3, description="连接后初始化")
            
            # 等待设置生效
            time.sleep(0.5)
            
            # 上使能所有关节
            print("上使能所有关节...")
            enable_success = hand.enable_all_motors_broadcast(True)
            print(f"上使能结果: {'成功' if enable_success else '失败'}")
            
            if not enable_success:
                print("上使能失败，无法继续测试")
                return
            
            # 等待使能稳定
            time.sleep(1)
            
            # 测试双手模式 - 30个关节位置
            print("\n--- 测试双手模式（非广播） ---")
            
            # 创建双手测试位置数据
            # 修改顺序：前15个是右手，后15个是左手
            right_positions = [math.radians(5.0)] * 15  # 右手所有关节5度（弧度制）
            left_positions = [math.radians(-5.0)] * 15   # 左手所有关节-5度（弧度制）
            double_positions = right_positions + left_positions
            
            print(f"设置双手位置数据: 右手{right_positions[:3]}..., 左手{left_positions[:3]}...")
            
            # 使用非广播模式
            success = hand.move_joints_pos(double_positions, speed=0.5, use_broadcast=False)
            print(f"双手非广播模式结果: {'成功' if success else '失败'}")
            
            time.sleep(2)
            
            # 使用广播模式
            print("\n--- 测试双手模式（广播模式） ---")
            success = hand.move_joints_pos(double_positions, speed=0.5, use_broadcast=True)
            print(f"双手广播模式结果: {'成功' if success else '失败'}")
            
            time.sleep(2)
            
            # 测试双手模式 - 自定义位置数据
            print("\n--- 测试双手模式（自定义位置） ---")
            
            # 右手：拇指弯曲，其他手指伸直（弧度制）
            right_custom = [
                # 拇指的3个关节
                0.0, math.radians(45.0), math.radians(45.0),
                # 其他手指的3个关节
                0.0, 0.0, 0.0,  # 食指
                0.0, 0.0, 0.0,  # 中指
                0.0, 0.0, 0.0,  # 无名指
                0.0, 0.0, 0.0   # 小指
            ]
            
            # 左手：食指弯曲，其他手指伸直（弧度制）
            left_custom = [
                # 拇指的3个关节
                0.0, 0.0, 0.0,
                # 食指的3个关节
                0.0, math.radians(45.0), math.radians(45.0),
                # 其他手指的3个关节
                0.0, 0.0, 0.0,  # 中指
                0.0, 0.0, 0.0,  # 无名指
                0.0, 0.0, 0.0   # 小指
            ]
            
            custom_double_positions = right_custom + left_custom
            print(f"设置自定义双手位置数据: 右手拇指弯曲，左手食指弯曲")
            success = hand.move_joints_pos(custom_double_positions, speed=0.5, use_broadcast=False)
            print(f"自定义双手位置结果: {'成功' if success else '失败'}")
            
            time.sleep(2)
            
            # 测试双手模式 - 手势执行
            print("\n--- 测试双手模式（手势执行） ---")
            
            # 双手运动（弧度制）
            double_fist = [math.radians(10.0)] * 30
            print("执行双手握拳手势...")
            success = hand.move_joints_pos(double_fist, speed=0.5, use_broadcast=False)
            print(f"双手握拳结果: {'成功' if success else '失败'}")
            
            time.sleep(2)
            
            # 双手回零
            double_open = [0.0] * 30
            print("执行双手张开手势...")
            success = hand.move_joints_pos(double_open, speed=0.5, use_broadcast=True)
            print(f"双手张开结果: {'成功' if success else '失败'}")
            
            time.sleep(2)
            
        else:
            print(f"GaiaHand 双手模式连接失败 (左手: {ports_config['left']}, 右手: {ports_config['right']})")
            
    except Exception as e:
        print(f"GaiaHand 双手模式测试失败: {e}")
    finally:
        if hand and hand.is_connected():
            print("回零...")
            hand.hand_zero()
            time.sleep(1)
            print("下使能所有关节...")
            disable_success = hand.enable_all_motors_broadcast(False)
            print(f"下使能结果: {'成功' if disable_success else '失败'}")
            hand.close()

def test_gaia_hand_smooth_transition(ports_config):
    """
    测试 GaiaHand 平滑过渡功能
    
    ⚠️ 注意：Gaia15已暂停维护，此函数仅用于兼容旧代码
    推荐使用 test_gaia20_hand_smooth_transition() 函数
    
    波特率配置：
    - 标准配置：230400
    - 注意：此函数中使用了921600，但标准配置应为230400
    """
    print("\n=== 测试 GaiaHand 平滑过渡功能 ===")
    
    if not ports_config or not ports_config['right']:
        print("未找到可用的右手串口，跳过平滑过渡测试")
        return
    
    hand = None
    try:
        # 创建右手 GaiaHand 实例
        # ⚠️ 注意：Gaia15标准配置应为230400，此处使用921600仅用于示例
        # 建议修改为：baudrate=230400
        hand = create_hand("gaia", "right", port=ports_config['right'], baudrate=921600)
        
        if hand.connect():
            print(f"GaiaHand 连接成功，开始平滑过渡测试 (串口: {ports_config['right']})")
            
            # 设置电机平滑等级（device_id=255表示广播所有电机，level=3）
            # 平滑等级范围：0-5，数值越大平滑效果越好
            set_motor_smooth_level(hand, device_id=255, level=3, description="连接后初始化")
            
            # 等待设置生效
            time.sleep(0.5)
            
            # 上使能所有关节
            print("上使能所有关节...")
            enable_success = hand.enable_all_motors_broadcast(True)
            print(f"上使能结果: {'成功' if enable_success else '失败'}")
            
            if not enable_success:
                print("上使能失败，无法继续测试")
                return
            
            # 等待使能稳定
            time.sleep(1)
            
            # 创建起始和结束位置（弧度制）
            start_positions = [0.0] * 15
            end_positions = [
                # 拇指的3个关节
                0.0, math.radians(27.0), math.radians(43.0),
                # 食指的3个关节
                0.0, math.radians(43.0), math.radians(56.0),
                # 中指的3个关节
                0.0, math.radians(33.0), math.radians(25.0),
                # 无名指的3个关节
                0.0, math.radians(28.0), math.radians(18.0),
                # 小指的3个关节
                0.0, math.radians(19.0), math.radians(26.0)
            ]
            
            print("执行平滑过渡：从伸直状态到弯曲状态")
            
            # 分5步过渡（非广播模式，更稳定）
            for i in range(6):
                t = i / 5.0
                positions = []
                for j in range(15):
                    pos = start_positions[j] + (end_positions[j] - start_positions[j]) * t
                    positions.append(pos)
                
                print(f"步骤 {i+1}/6: 过渡进度 {t*100:.1f}%")
                hand.move_joints_pos(positions, speed=0.5, use_broadcast=True)
                time.sleep(0.05)
                current_positions = hand.get_joint_positions()
                print(f"当前关节位置=====================: {current_positions}")

            print("平滑过渡完成")
            
            time.sleep(2)
            
            # 反向过渡：从弯曲状态到伸直状态
            print("执行反向过渡：从弯曲状态到伸直状态")
            
            for i in range(10):
                t = i / 10.0
                positions = []
                for j in range(15):
                    pos = end_positions[j] + (start_positions[j] - end_positions[j]) * t
                    positions.append(pos)
                
                print(f"步骤 {i+1}/6: 过渡进度 {t*100:.1f}%")
                hand.move_joints_pos(positions, speed=0.5, use_broadcast=True)
                time.sleep(0.05)
                current_positions = hand.get_joint_positions()
                print(f"当前关节位置======================: {current_positions}")
            
            print("反向过渡完成")

            time.sleep(2)
            
        else:
            print(f"GaiaHand 连接失败 (串口: {ports_config['right']})")
            
    except Exception as e:
        print(f"GaiaHand 平滑过渡测试失败: {e}")
    finally:
        if hand and hand.is_connected():
            print("回零...")
            hand.hand_zero()
            time.sleep(1)
            print("下使能所有关节...")
            disable_success = hand.enable_all_motors_broadcast(False)
            print(f"下使能结果: {'成功' if disable_success else '失败'}")
            hand.close()

def test_reset_pose_zero(ports_config):
    """
    测试手部回零功能（Gaia15）
    
    ⚠️ 注意：Gaia15已暂停维护，此函数仅用于兼容旧代码
    推荐使用 test_gaia20_hand_reset_zero() 函数
    
    波特率配置：230400（标准配置）
    """
    print("\n=== 测试手部回零功能 ===")
    
    if not ports_config or not ports_config['right']:
        print("未找到可用的右手串口，跳过回零测试")
        return
    
    hand = None
    try:
        # 创建右手 GaiaHand 实例
        hand = create_hand("gaia", "right", port=ports_config['right'])
        
        if hand.connect():
            print(f"GaiaHand 连接成功，开始回零测试 (串口: {ports_config['right']})")
            
            # 设置电机平滑等级（device_id=255表示广播所有电机，level=3）
            # 平滑等级范围：0-5，数值越大平滑效果越好
            set_motor_smooth_level(hand, device_id=255, level=3, description="连接后初始化")
            
            # 等待设置生效
            time.sleep(0.5)
            
            # 上使能所有关节
            print("上使能所有关节...")
            enable_success = hand.enable_all_motors_broadcast(True)
            print(f"上使能结果: {'成功' if enable_success else '失败'}")
            
            if not enable_success:
                print("上使能失败，无法继续测试")
                return
            
            # 等待使能稳定
            time.sleep(2)
            
            # 执行回零操作
            print("执行回零操作...")
            hand.hand_zero()
            print("回零操作完成")
            
            time.sleep(2)
            
        else:
            print(f"GaiaHand 连接失败 (串口: {ports_config['right']})")
            
    except Exception as e:
        print(f"GaiaHand 回零测试失败: {e}")
    finally:
        if hand and hand.is_connected():
            print("回零...")
            hand.hand_zero()
            time.sleep(1)
            print("下使能所有关节...")
            disable_success = hand.enable_all_motors_broadcast(False)
            print(f"下使能结果: {'成功' if disable_success else '失败'}")
            hand.close()


def main():
    """
    主测试函数
    
    ⭐ 推荐使用 Gaia20（16关节版本），当前主要维护版本
    ⚠️ Gaia15（15关节版本）已暂停维护，相关测试函数仅用于兼容旧代码
    
    波特率配置说明：
    - Gaia15: 230400（标准配置）
    - Gaia20不带主控板: 230400（默认配置）
    - Gaia20带主控板: 921600（高性能配置）
    
    使用说明：
    1. 根据您的硬件配置选择合适的测试函数
    2. 取消注释相应的测试函数来运行测试
    3. 默认优先运行Gaia20测试函数
    """
    print("开始测试 GaiaHand 功能")
    print("=" * 50)
    print("⭐ 推荐使用 Gaia20（16关节版本），当前主要维护版本")
    print("⚠️ Gaia15（15关节版本）已暂停维护")
    print("=" * 50)

    # 设置日志等级（可选：取消注释 test_log_management() 测试日志管理功能）
    # test_log_management()
    set_log_level('INFO') # DEBUG INFO WARNING ERROR CRITICAL
    # enable_all_logs()
    # disable_all_logs()
    # set_both_output()

    # 检测串口
    ports_config = detect_serial_ports()
    
    if not ports_config:
        print("串口检测失败，无法进行测试")
        return
    
    print(f"\n使用串口配置:")
    print(f"  左手: {ports_config['left']}")
    print(f"  右手: {ports_config['right']}")
    print(f"  可用串口: {ports_config['available']}")
    
    print("\n波特率配置说明：")
    print("  - Gaia15: 230400（标准配置）")
    print("  - Gaia20不带主控板: 230400（默认配置）")
    print("  - Gaia20带主控板: 921600（高性能配置）")

    # ==================== GaiaHand20（16关节）测试 ⭐ 推荐使用 ====================
    print("\n" + "=" * 50)
    print("GaiaHand20（16关节）测试 ⭐ 推荐使用")
    print("=" * 50)

    # 测试 GaiaHand20 创建手部实例
    # test_gaia20_hand_create_hand(ports_config)
    
    # 测试 GaiaHand20 状态获取（连接状态、关节位置、电机状态）
    # test_gaia20_hand_get_status(ports_config)

    # 测试 GaiaHand20 关节限位接口（默认不连接硬件、不发送运动指令）
    # test_gaia20_hand_joint_limits(ports_config)
    # 如需连接硬件验证超限夹紧，可使用：
    # test_gaia20_hand_joint_limits(ports_config, connect_for_motion=True)
    
    # 测试 GaiaHand20 单手模式获取位置（默认启用）
    # test_gaia20_hand_get_joint_positions(ports_config)

    # 测试 GaiaHand20 单手模式 get_joints_pos_vel（协议字典 3=位置 5=速度；可与上项对照连接配置）
    test_gaia20_hand_get_joints_pos_vel(ports_config)
    
    # 测试 GaiaHand20 单手模式（列表格式）- 波特率：230400（不带主控板）
    # test_gaia20_hand_move_joints_pos_list(ports_config)
    
    # 测试 GaiaHand20 单手模式（字典格式）- 波特率：230400（不带主控板）
    # test_gaia20_hand_move_joints_pos_dict(ports_config)
    
    # 测试 GaiaHand20 双手模式（列表格式）- 波特率：230400（不带主控板）
    # test_gaia20_hand_double_move_joints_pos(ports_config)
    
    # 测试 GaiaHand20 双手模式（字典格式）- 波特率：230400（不带主控板）
    # test_gaia20_hand_double_move_joints_pos_dict(ports_config)
    
    # 测试 GaiaHand20 双手模式获取位置 - 波特率：230400（不带主控板）
    # test_gaia20_hand_double_get_joint_positions(ports_config)
    
    # 测试 GaiaHand20 平滑过渡 - 波特率：921600（带主控板）
    # test_gaia20_hand_smooth_transition(ports_config)
    
    # 测试 GaiaHand20 回零位 - 波特率：921600（带主控板）
    # test_gaia20_hand_reset_zero(ports_config)
    
    # ==================== GaiaHand（15关节）测试 ⚠️ 暂停维护 ====================
    # print("\n" + "=" * 50)
    # print("GaiaHand（15关节）测试 ⚠️ 暂停维护，仅用于兼容")
    # print("=" * 50)
    
    # 测试回零位 - 波特率：230400（标准配置）
    # test_reset_pose_zero(ports_config)
    
    # 测试 GaiaHand 单手模式 - 波特率：921600（示例中，但标准配置应为230400）
    # test_gaia_hand_move_joints_pos(ports_config)
    
    # 测试 GaiaHand 双手模式 - 波特率：230400（标准配置）
    # test_gaia_hand_double_move_joints_pos(ports_config)
    
    # 测试 GaiaHand 平滑过渡 - 波特率：921600（示例中，但标准配置应为230400）
    # test_gaia_hand_smooth_transition(ports_config)
    
    # print("\n" + "=" * 50)
    # print("所有测试完成")
    # print("⭐ 推荐使用 Gaia20（16关节版本）进行开发")

if __name__ == "__main__":
    main()
