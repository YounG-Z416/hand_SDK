#!/usr/bin/env python3
"""
PantheonHand 控制示例文件

功能说明：
- 测试 PantheonHand 的 move_joints_pos 和 get_joint_positions 功能
- 支持单手（right/left）和双手（double）模式
- 关节位置控制（列表格式和字典格式）
- 指令6格式（单关节控制）
- 紧绳操作
- 手势执行和回零操作
- 错误处理和资源清理
- 日志管理功能（enable_all_logs、disable_all_logs、set_log_level 等，可通过 test_log_management() 测试）

CAN 配置说明：
- PantheonHand 通过 CAN 总线通信，需配置 dev_type、channel、arbitration_bitrate 等
- 双手模式：右手 CAN 通道 0，左手 CAN 通道 1（可自定义）
- 默认配置：VCI_USBCAN2(41)，1Mbps 仲裁速率

使用说明：
1. 根据硬件连接配置 CAN 参数（可选，使用默认配置时无需传入）
2. 在 main() 函数中取消注释相应的测试函数来运行测试
3. 双手模式需要双手硬件支持
"""

import time
import sys
import os
import math

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hand import create_hand, FingerType

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


def get_default_can_config():
    """
    获取默认 CAN 配置

    Returns:
        dict: CAN 配置，可用于 create_hand(..., can_config=config)
    """
    return {
        'dev_type': 41,           # VCI_USBCAN2
        'channel': 0,             # CAN 通道 (0=CAN1, 1=CAN2)
        'arbitration_bitrate': 1000000,  # 1Mbps 仲裁速率
        'data_bitrate': 5000000,  # 5Mbps 数据速率
        'canfd_mode': 0
    }


def test_log_management():
    """测试日志管理功能"""
    print("\n" + "=" * 60)
    print("=== 测试日志管理功能 ===")

    print("\n1. 启用所有日志...")
    enable_all_logs()
    print("✅ 已启用所有日志")

    print("\n2. 设置日志级别为 DEBUG...")
    set_log_level('DEBUG')
    print("✅ 已设置日志级别为 DEBUG")

    print("\n3. 测试不同输出方式...")
    set_console_only()
    print("   ✅ 已设置为仅控制台输出")
    set_file_only()
    print("   ✅ 已设置为仅文件输出")
    set_both_output()
    print("   ✅ 已设置为控制台+文件输出")

    print("\n4. 测试禁用所有日志...")
    disable_all_logs()
    print("❌ 已禁用所有日志")

    print("\n   测试禁用日志后的效果（以下日志应该不会显示）:")
    from hand.core import get_logger
    test_logger = get_logger('test.disable_logs')
    test_logger.info("这条 INFO 日志应该不会显示")
    test_logger.warning("这条 WARNING 日志应该不会显示")
    test_logger.error("这条 ERROR 日志应该不会显示")
    print("   ✅ 禁用日志测试完成")

    print("\n5. 测试特定脚本的日志控制...")
    log_controller.set_script_logging('pantheonhand.motor', enabled=True, level='WARNING')
    print("✅ 已设置 pantheonhand.motor 为 WARNING 级别")

    print("\n6. 当前日志状态:")
    show_log_status()

    print("\n7. 重新启用日志以便后续测试...")
    enable_all_logs()
    set_log_level('INFO')
    set_both_output()
    print("✅ 已重新启用日志")


def test_pantheon_hand_connection(can_config=None):
    """
    测试 PantheonHand 连接功能

    Args:
        can_config: 可选，CAN 配置字典。为 None 时使用默认配置
    """
    print("\n=== 测试 PantheonHand 连接功能 ===")

    hand = None
    try:
        hand = create_hand("pantheon", "right", can_config=can_config or {})

        if hand.connect():
            print("✅ PantheonHand 右手连接成功")
            print(f"连接状态: {'已连接' if hand.is_connected() else '未连接'}")
            print(f"手部类型: {hand.hand_type.value}")
            print(f"手部侧边: {hand.hand_side_name}")
            print(f"是否为右手: {hand.is_right_hand}")
            return True
        else:
            print("❌ PantheonHand 右手连接失败")
            return False

    except Exception as e:
        print(f"❌ PantheonHand 连接测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if hand and hand.is_connected():
            print("回零...")
            hand.hand_zero()
            time.sleep(1)
            print("下使能所有关节...")
            disable_success = hand.enable_all_motors(False)
            print(f"下使能结果: {'成功' if disable_success else '失败'}")
            hand.close()


def test_pantheon_hand_rope_tight(can_config=None):
    """
    测试 PantheonHand 紧绳功能

    包含：全手指紧绳、单手指紧绳

    Args:
        can_config: 可选，CAN 配置字典
    """
    print("\n=== 测试 PantheonHand 紧绳功能 ===")

    hand = None
    try:
        hand = create_hand("pantheon", "right", can_config=can_config or {})

        if hand.connect():
            print("PantheonHand 连接成功，开始测试紧绳功能")
            time.sleep(1)

            hand.enable_all_motors()
            time.sleep(2)

            print("\n--- 测试1：全手指紧绳 ---")
            try:
                hand.rope_tight()
                print("全手指紧绳命令已发送")
                time.sleep(5)
            except Exception as e:
                print(f"全手指紧绳失败: {e}")

            print("\n--- 测试2：单手指紧绳（拇指） ---")
            try:
                hand.rope_tight(FingerType.THUMB)
                print("拇指紧绳命令已发送")
                time.sleep(3)
            except Exception as e:
                print(f"拇指紧绳失败: {e}")

            print("\n--- 测试3：单手指紧绳（食指） ---")
            try:
                hand.rope_tight(FingerType.INDEX)
                print("食指紧绳命令已发送")
                time.sleep(3)
            except Exception as e:
                print(f"食指紧绳失败: {e}")

            print("\n--- 回零 ---")
            success = hand.hand_zero()
            print(f"回零结果: {'成功' if success else '失败'}")

            return True
        else:
            print("PantheonHand 连接失败")
            return False

    except Exception as e:
        print(f"PantheonHand 紧绳测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if hand and hand.is_connected():
            print("回零...")
            hand.hand_zero()
            time.sleep(1)
            print("下使能所有关节...")
            disable_success = hand.enable_all_motors(False)
            print(f"下使能结果: {'成功' if disable_success else '失败'}")
            hand.close()


def test_pantheon_hand_get_joint_positions(can_config=None):
    """
    测试 PantheonHand 的 get_joint_positions 功能

    Args:
        can_config: 可选，CAN 配置字典
    """
    print("\n=== 测试 PantheonHand get_joint_positions 功能 ===")

    hand = None
    try:
        hand = create_hand("pantheon", "right", can_config=can_config or {})

        if hand.connect():
            print("PantheonHand 连接成功，开始测试 get_joint_positions")

            print("\n--- 测试获取所有关节位置 ---")
            all_positions = hand.get_joint_positions()
            print(f"所有关节位置: {all_positions}")
            print(f"位置数据类型: {type(all_positions)}")
            if hasattr(all_positions, '__len__'):
                print(f"位置数据长度: {len(all_positions)}")

            return True
        else:
            print("PantheonHand 连接失败")
            return False

    except Exception as e:
        print(f"PantheonHand get_joint_positions 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if hand and hand.is_connected():
            print("回零...")
            hand.hand_zero()
            time.sleep(1)
            print("下使能所有关节...")
            disable_success = hand.enable_all_motors(False)
            print(f"下使能结果: {'成功' if disable_success else '失败'}")
            hand.close()


def test_pantheon_hand_move_joints_pos_list(can_config=None):
    """
    测试 PantheonHand 的 move_joints_pos 功能（列表格式，15关节）

    Args:
        can_config: 可选，CAN 配置字典
    """
    print("\n=== 测试 PantheonHand move_joints_pos 功能（列表格式） ===")

    hand = None
    try:
        hand = create_hand("pantheon", "right", can_config=can_config or {})

        if hand.connect():
            print("PantheonHand 连接成功，开始测试 move_joints_pos（列表格式）")
            time.sleep(1)

            hand.enable_all_motors()
            time.sleep(2)

            print("\n--- 测试1：设置所有关节为0弧度 ---")
            zero_positions = [0.0] * 15
            success = hand.move_joints_pos(zero_positions, speed=0.5)
            print(f"设置0弧度结果: {'成功' if success else '失败'}")
            if success:
                time.sleep(2)
                current_positions = hand.get_joint_positions()
                print(f"当前位置: {current_positions}")

            print("\n--- 测试2：设置自定义位置 ---")
            custom_positions = [
                math.radians(40), math.radians(10), math.radians(10),
                0.0, math.radians(10), math.radians(10),
                0.0, math.radians(10), math.radians(10),
                0.0, math.radians(10), math.radians(10),
                0.0, math.radians(10), math.radians(10)
            ]
            success = hand.move_joints_pos(custom_positions, speed=0.5)
            print(f"设置自定义位置结果: {'成功' if success else '失败'}")
            time.sleep(3)

            print("\n--- 测试3：回零测试 ---")
            success = hand.hand_zero()
            print(f"回零结果: {'成功' if success else '失败'}")
            if success:
                time.sleep(2)
                current_positions = hand.get_joint_positions()
                print(f"回零后位置: {current_positions}")

            return True
        else:
            print("PantheonHand 连接失败")
            return False

    except Exception as e:
        print(f"PantheonHand move_joints_pos（列表格式）测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if hand and hand.is_connected():
            print("回零...")
            hand.hand_zero()
            time.sleep(1)
            print("下使能所有关节...")
            disable_success = hand.enable_all_motors(False)
            print(f"下使能结果: {'成功' if disable_success else '失败'}")
            hand.close()


def test_pantheon_hand_move_joints_pos_dict(can_config=None):
    """
    测试 PantheonHand 的 move_joints_pos 功能（字典格式）

    包含：字典格式设置、指令6格式、逐个手指控制、回零

    Args:
        can_config: 可选，CAN 配置字典
    """
    print("\n=== 测试 PantheonHand move_joints_pos 功能（字典格式） ===")

    hand = None
    try:
        hand = create_hand("pantheon", "right", can_config=can_config or {})

        if hand.connect():
            print("PantheonHand 连接成功，开始测试 move_joints_pos（字典格式）")
            time.sleep(1)

            hand.enable_all_motors()
            time.sleep(2)

            print("\n--- 测试1：字典格式设置右手位置 ---")
            right_hand_data = {
                1: [1.5, math.radians(10), math.radians(10)],
                2: [0.0, math.radians(10), math.radians(10)],
                3: [0.0, math.radians(10), math.radians(10)],
                4: [0.0, math.radians(10), math.radians(10)],
                5: [0.0, math.radians(10), math.radians(10)]
            }
            positions_dict = {1: right_hand_data}
            success = hand.move_joints_pos(positions_dict, speed=0.01)
            print(f"字典格式设置结果: {'成功' if success else '失败'}")
            if success:
                time.sleep(2)
                print(f"当前位置: {hand.get_joint_positions()}")

            print("\n--- 测试2：指令6格式（单关节控制） ---")
            command_6_data = [1, 2, 1, math.radians(30)]  # 右手，食指，关节1，30度
            positions_dict = {6: command_6_data}
            success = hand.move_joints_pos(positions_dict, speed=1)
            print(f"指令6设置结果: {'成功' if success else '失败'}")
            if success:
                time.sleep(1)
                print(f"当前位置: {hand.get_joint_positions()}")

            print("\n--- 测试3：逐个手指控制 ---")
            for finger_id in range(1, 6):
                finger_data = {finger_id: [0.0, math.radians(20), math.radians(30)]}
                positions_dict = {1: finger_data}
                success = hand.move_joints_pos(positions_dict, speed=1)
                print(f"手指{finger_id}控制结果: {'成功' if success else '失败'}")
                time.sleep(1)

            print("\n--- 测试4：回零 ---")
            zero_data = {fid: [0.0, 0.0, 0.0] for fid in range(1, 6)}
            positions_dict = {1: zero_data}
            success = hand.move_joints_pos(positions_dict, speed=1)
            print(f"回零结果: {'成功' if success else '失败'}")

            return True
        else:
            print("PantheonHand 连接失败")
            return False

    except Exception as e:
        print(f"PantheonHand move_joints_pos（字典格式）测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if hand and hand.is_connected():
            print("回零...")
            hand.hand_zero()
            time.sleep(1)
            print("下使能所有关节...")
            disable_success = hand.enable_all_motors(False)
            print(f"下使能结果: {'成功' if disable_success else '失败'}")
            hand.close()


def test_pantheon_hand_double_mode(can_config=None):
    """
    测试 PantheonHand 双手模式

    包含：列表格式、字典格式、回零

    Args:
        can_config: 可选，双手 CAN 配置。为 None 时使用默认（单 CAN 设备双手）
    """
    print("\n=== 测试 PantheonHand 双手模式 ===")

    hand = None
    try:
        hand = create_hand("pantheon", "double", can_config=can_config or {})

        if hand.connect():
            print("✅ PantheonHand 双手模式连接成功")
            time.sleep(1)

            hand.enable_all_motors()
            time.sleep(2)

            print("\n--- 测试获取双手位置 ---")
            all_positions = hand.get_joint_positions()
            print(f"双手位置: {all_positions}")

            print("\n--- 测试双手模式列表格式 ---")
            right_positions = [math.radians(0)] * 15
            left_positions = [math.radians(-15)] * 15
            double_positions = right_positions + left_positions
            success = hand.move_joints_pos(double_positions, speed=0.5)
            print(f"双手列表格式设置结果: {'成功' if success else '失败'}")
            if success:
                time.sleep(2)
                print(f"当前位置: {hand.get_joint_positions()}")

            print("\n--- 测试双手模式字典格式 ---")
            right_hand_data = {
                1: [0.0, math.radians(10), math.radians(10)],
                2: [0.0, math.radians(10), math.radians(10)],
                3: [0.0, math.radians(10), math.radians(10)],
                4: [0.0, math.radians(10), math.radians(10)],
                5: [0.0, math.radians(10), math.radians(10)]
            }
            left_hand_data = {
                1: [0.0, math.radians(-20), math.radians(-30)],
                2: [0.0, math.radians(-25), math.radians(-35)],
                3: [0.0, math.radians(-20), math.radians(-25)],
                4: [0.0, math.radians(-15), math.radians(-20)],
                5: [0.0, math.radians(-10), math.radians(-15)]
            }
            positions_dict = {1: right_hand_data, 2: left_hand_data}
            success = hand.move_joints_pos(positions_dict, speed=0.5)
            print(f"双手字典格式设置结果: {'成功' if success else '失败'}")
            if success:
                time.sleep(2)
                print(f"当前位置: {hand.get_joint_positions()}")

            print("\n--- 测试双手回零 ---")
            success = hand.hand_zero()
            print(f"双手回零结果: {'成功' if success else '失败'}")
            time.sleep(3)

            return True
        else:
            print("❌ PantheonHand 双手模式连接失败")
            return False

    except Exception as e:
        print(f"❌ PantheonHand 双手模式测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if hand and hand.is_connected():
            print("回零...")
            hand.hand_zero()
            time.sleep(1)
            print("下使能所有关节...")
            disable_success = hand.enable_all_motors(False)
            print(f"下使能结果: {'成功' if disable_success else '失败'}")
            print("正在关闭双手连接...")
            hand.close()
            print("✅ 双手连接已关闭")


def test_pantheon_hand_individual_control(can_config=None):
    """
    测试 PantheonHand 单个关节/手指控制

    Args:
        can_config: 可选，CAN 配置字典
    """
    print("\n=== 测试 PantheonHand 单个关节控制 ===")

    hand = None
    try:
        hand = create_hand("pantheon", "right", can_config=can_config or {})

        if hand.connect():
            print("PantheonHand 连接成功，开始测试单个关节控制")
            time.sleep(1)

            hand.enable_all_motors()
            time.sleep(2)

            print("\n--- 测试控制单个手指 ---")
            finger_positions = [0.0, math.radians(30), math.radians(45)]
            success = hand.control_single_finger(0, finger_positions)
            print(f"控制拇指结果: {'成功' if success else '失败'}")
            if success:
                time.sleep(1)
                print(f"当前位置: {hand.get_joint_positions()}")

            print("\n--- 测试控制单个关节 ---")
            success = hand.control_finger_joint(1, 0, math.radians(20))
            print(f"控制食指第1个关节结果: {'成功' if success else '失败'}")
            if success:
                time.sleep(1)
                print(f"当前位置: {hand.get_joint_positions()}")

            print("\n--- 测试控制多个手指 ---")
            finger_positions_dict = {
                0: [0.0, math.radians(15), math.radians(25)],
                1: [0.0, math.radians(20), math.radians(30)],
                2: [0.0, math.radians(15), math.radians(20)]
            }
            success = hand.control_multiple_fingers(finger_positions_dict)
            print(f"控制多个手指结果: {'成功' if success else '失败'}")

            print("\n--- 测试回零 ---")
            success = hand.hand_zero()
            print(f"回零结果: {'成功' if success else '失败'}")

            return True
        else:
            print("PantheonHand 连接失败")
            return False

    except Exception as e:
        print(f"PantheonHand 单个关节控制测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if hand and hand.is_connected():
            print("回零...")
            hand.hand_zero()
            time.sleep(1)
            print("下使能所有关节...")
            disable_success = hand.enable_all_motors(False)
            print(f"下使能结果: {'成功' if disable_success else '失败'}")
            hand.close()


def test_pantheon_hand_motor_status(can_config=None):
    """
    测试 PantheonHand 电机状态获取

    Args:
        can_config: 可选，CAN 配置字典
    """
    print("\n=== 测试 PantheonHand 电机状态获取 ===")

    hand = None
    try:
        hand = create_hand("pantheon", "right", can_config=can_config or {})

        if hand.connect():
            print("PantheonHand 连接成功，开始测试电机状态获取")
            time.sleep(1)

            hand.enable_all_motors()
            time.sleep(2)

            print("\n--- 测试获取所有电机状态 ---")
            all_status = hand.get_motor_status()
            print(f"所有电机状态: {all_status}")

            print("\n--- 测试获取指定电机状态 ---")
            for motor_id in range(5):
                try:
                    motor_status = hand.get_motor_status(motor_id)
                    print(f"电机{motor_id}状态: {motor_status}")
                except Exception as e:
                    print(f"获取电机{motor_id}状态失败: {e}")

            return True
        else:
            print("PantheonHand 连接失败")
            return False

    except Exception as e:
        print(f"PantheonHand 电机状态获取测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if hand and hand.is_connected():
            print("回零...")
            hand.hand_zero()
            time.sleep(1)
            print("下使能所有关节...")
            disable_success = hand.enable_all_motors(False)
            print(f"下使能结果: {'成功' if disable_success else '失败'}")
            hand.close()


def main():
    """
    主测试函数

    使用说明：
    1. 根据硬件配置选择 CAN 配置（可选）
    2. 取消注释相应的测试函数来运行测试
    3. 双手模式需要双手硬件支持
    """
    print("开始测试 PantheonHand 功能")
    print("=" * 60)

    # 设置日志
    # test_log_management()
    set_log_level('INFO')
    enable_all_logs()
    set_both_output()

    # 获取 CAN 配置（可选，根据硬件修改 channel 等参数）
    can_config = get_default_can_config()

    # ==================== 单手模式测试 ====================
    print("\n" + "=" * 60)
    print("PantheonHand 单手模式测试")
    print("=" * 60)

    # 测试连接功能
    # test_pantheon_hand_connection(can_config)

    # 测试紧绳功能
    # test_pantheon_hand_rope_tight(can_config)

    # 测试获取关节位置
    # test_pantheon_hand_get_joint_positions(can_config)

    # 测试 move_joints_pos（列表格式）
    # test_pantheon_hand_move_joints_pos_list(can_config)

    # 测试 move_joints_pos（字典格式）
    test_pantheon_hand_move_joints_pos_dict(can_config)

    # 测试单个关节控制
    # test_pantheon_hand_individual_control(can_config)

    # 测试电机状态获取
    # test_pantheon_hand_motor_status(can_config)

    # ==================== 双手模式测试 ====================
    print("\n" + "=" * 60)
    print("PantheonHand 双手模式测试（需要双手硬件）")
    print("=" * 60)

    # test_pantheon_hand_double_mode(can_config)

    print("\n" + "=" * 60)
    print("所有 PantheonHand 测试完成")


if __name__ == "__main__":
    main()
