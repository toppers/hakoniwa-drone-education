#include "hako_module_drone_controller_impl.h"
#include "drone_controller.hpp"
#include <algorithm>
#include <iostream>

const char* hako_module_drone_controller_impl_get_name(void)
{
    return "DroneController";
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

    double target_pos_x = in->target_pos_x;
    double target_pos_y = in->target_pos_y;
    double target_pos_z = -in->target_pos_z;
    double target_velocity = in->target_velocity;
    double target_angle = in->target_yaw_deg;

    /*
     * 高度制御
     */
    DroneALtInputType alt_in(pos, velocity, target_pos_z);
    DroneAltOutputType alt_out = ctrl->alt->run(alt_in);
    /*
     * 機首方向制御
     */
    DroneHeadingControlInputType head_in(euler, target_angle);
    DroneHeadingControlOutputType head_out = ctrl->head->run(head_in);
    /*
     * 水平制御
     */
    DronePosInputType pos_in(pos, euler, target_pos_x, target_pos_y, target_velocity);
    DronePosOutputType pos_out = ctrl->pos->run(pos_in);
    /*
     * 姿勢角度制御
     */
    //TODO
    /*
     * 姿勢角速度制御
     */
    //TODO

    /*
     * 出力
     */
    out.thrust = alt_out.thrust;
    out.torque_x = 0;
    out.torque_y = 0;
    out.torque_z = 0;
    return out;
}


