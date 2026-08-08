#!/usr/bin/env python3
"""
ARX LIFT 2026 手柄控制程序

使用手柄控制机器人的升降和底盘运动
"""

import time
from liftlib import InterfacesPy, RobotType
from liftlib import Joystick


def main():
    # 配置
    CAN_ROBOT = 'can5'  # 机器人CAN接口
    ROBOT_TYPE = RobotType.LIFT2026_4310_3519

    CAN_JOYSTICK = 'can6'  # 手柄CAN接口

    print("正在初始化机器人和手柄...")

    try:
        # 初始化机器人
        robot = InterfacesPy(CAN_ROBOT, ROBOT_TYPE)
        print(f"✓ 机器人已连接 (CAN: {CAN_ROBOT})")

        # 初始化手柄
        joy = Joystick(CAN_JOYSTICK)
        print(f"✓ 手柄已连接 (CAN: {CAN_JOYSTICK})")


        # 控制参数
        robot.loop()
        lift_height = robot.get_height()  # 启动时的升降高度 (增量式基准, 无需复位)
        set_height_cmd = 0.0              # 距启动时增加的高度值 (必须在循环外初始化)
        last_time = time.time()

        # 手感参数
        LIFT_RATE = 0.04   # m/s   — 摇杆推满时升降目标变化速率 (平台极限≈0.034)
        V_XY_MAX = 0.15    # m/s   — 摇杆推满时的平移速度
        W_Z_MAX = 0.45     # rad/s — 旋转速度
        W_Z_GATE = 0.5     # 旋转轴推过半程才生效 (防误触)

        # 控制循环
        while True:

            axes = joy.get_axes()        # [左Y, 左X, 0.0, 右Y, 右X], 范围 [-1,1], 含死区
            buttons = joy.get_buttons()  # 4 个按钮 (半字节值)

            # 本拍时长 (积分用); 异常跳变不积分
            now = time.time()
            dt = now - last_time
            last_time = now
            if dt > 1.0:
                dt = 0.0

            # 升降: 左摇杆 Y (axes[0]) 增量调目标, 乘 dt 才与循环频率无关
            set_height_cmd += axes[0] * LIFT_RATE * dt
            set_lift_height = max(0.0, min(0.38, lift_height + set_height_cmd))
            set_height_cmd = set_lift_height - lift_height   # 回写, 防积分饱和
            robot.set_height(set_lift_height)

            # 底盘: 右摇杆平移 (Y=前后 X=左右), 左摇杆 X 旋转 (过半程生效)
            w_z = axes[1] * W_Z_MAX if abs(axes[1]) > W_Z_GATE else 0.0
            robot.set_chassis_cmd(axes[3] * V_XY_MAX, axes[4] * V_XY_MAX, w_z, 1)

            
            # 轮速控制，设置模式为3
            # robot.set_chassis_cmd(0,0,0,3)
            # robot.set_wheel_vel(0,0,0,0)


            # 获取高度值
            get_chassis_height=robot.get_height()

            # 轮速获取
            get_wheel_vel=robot.get_wheel_vel()

            print(f"当前高度: {get_chassis_height}")
            print(f"轮速: {get_wheel_vel}")






            # 执行控制循环
            robot.loop()
            time.sleep(0.0025)

    except KeyboardInterrupt:
        print("\n\n正在退出...")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
