#include "hako_module_drone_controller_impl.h"
#include "drone_controller.hpp"
#include <algorithm>
#include <iostream>

const char* hako_module_drone_controller_impl_get_name(void)
{
    return "AltSpeedController";
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
    FlightControllerInputVelocityType velocity = {in->u, in->v, -in->w};
    FlightControllerInputAngularRateType angular_rate = {in->p, in->q, in->r};

    double target_spd_z = -in->target.throttle.power;

    /*
     * 高度制御
     */
    DroneAltSpdInputType alt_in(euler, velocity, target_spd_z);
    DroneAltOutputType alt_out = ctrl->alt->run_spd(alt_in);

    /*
     * 出力
     */
    out.thrust = alt_out.thrust;
    out.torque_x = 0;
    out.torque_y = 0;
    out.torque_z = 0;
    return out;
}


