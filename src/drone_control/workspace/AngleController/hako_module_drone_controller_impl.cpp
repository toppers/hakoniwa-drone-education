#include "hako_module_drone_controller_impl.h"
#include "drone_controller.hpp"
#include <algorithm>
#include <iostream>

const char* hako_module_drone_controller_impl_get_name(void)
{
    return "AngleController";
}


void* hako_module_drone_controller_impl_create_context(void*)
{
    return (void*)new DroneController();
}

int hako_module_drone_controller_impl_is_operation_doing(void *context)
{
    return true;
}

int hako_module_drone_controller_impl_init(void*)
{
    return 0;
}
mi_drone_control_out_t hako_module_drone_controller_impl_run(mi_drone_control_in_t *in)
{
    DroneController* ctrl = (DroneController*)in->context;
    mi_drone_control_out_t out = {};
    /*
     * 入力
     * 補足：z軸は、わかりやすさを重視しして符号を反転する。
     */
    FlightControllerInputEulerType euler = {in->euler_x, in->euler_y, in->euler_z};
    FlightControllerInputPositionType pos = {in->pos_x, in->pos_y, -in->pos_z};
    FlightControllerInputVelocityType velocity = {in->u, in->v, -in->w};
    FlightControllerInputAngularRateType angular_rate = {in->p, in->q, in->r};

    double target_pos_z = in->target.throttle.power;

    /*
     * 高度制御
     */
    DroneAltInputType alt_in(pos, velocity, target_pos_z);
    DroneAltOutputType alt_out = ctrl->alt->run(alt_in);
    /*
     * 機首方向制御
     */
    DroneHeadingControlInputType head_in(euler, 0.0);
    DroneHeadingControlOutputType head_out = ctrl->head->run(head_in);
    /*
     * 姿勢角度制御
     */
    double target_roll = in->target.attitude.roll;
    double target_pitch = in->target.attitude.pitch;
    double target_yaw_rate = head_out.target_yaw_rate;
    DroneAngleInputType angle_in(euler, angular_rate, target_roll, target_pitch, target_yaw_rate);
    DroneAngleOutputType angle_out = ctrl->angle->run(angle_in);
    /*
     * 出力
     */
    out.thrust = alt_out.thrust;
    out.torque_x = angle_out.p;
    out.torque_y = angle_out.q;
    out.torque_z = angle_out.r;
    return out;
}


