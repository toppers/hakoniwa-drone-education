#include "hako_module_drone_controller_impl.h"
#include "drone_controller.hpp"
#include <algorithm>
#include <iostream>

const char* hako_module_drone_controller_impl_get_name(void)
{
    return "PlantController";
}


void* hako_module_drone_controller_impl_create_context(void*)
{
    return nullptr;
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
    mi_drone_control_out_t out = {};
    /*
     * 出力
     */
#if 0
    out.thrust   = in->target.throttle.power;
    out.torque_x = in->target.attitude.roll;
    out.torque_y = in->target.attitude.pitch;
    out.torque_z = in->target.direction_velocity.r;
#else
    out.rotor.num = 4;
    out.rotor.controls[0] = in->target.direction_velocity.r / in->max_rpm;
    out.rotor.controls[1] = in->target.throttle.power / in->max_rpm;
    out.rotor.controls[2] = in->target.attitude.roll / in->max_rpm;
    out.rotor.controls[3] = in->target.attitude.pitch / in->max_rpm;
#endif
    return out;
}


