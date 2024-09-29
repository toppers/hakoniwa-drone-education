#ifndef _DRONE_ALT_CONTROLLER_HPP_
#define _DRONE_ALT_CONTROLLER_HPP_

#include "drone_pid_control.hpp"
#include "flight_controller_types.hpp"
#include "hako_controller_param_loader.hpp"
#include <memory>

struct DroneALtInputType {
    FlightControllerInputPositionType pos;
    FlightControllerInputVelocityType spd;
    double target_altitude;
    DroneALtInputType() : pos(), spd() {}
    DroneALtInputType(FlightControllerInputPositionType p, FlightControllerInputVelocityType s, double t_a) : pos(p), spd(s), target_altitude(t_a) {}    
};

struct DroneAltOutputType {
    double thrust;
    DroneAltOutputType() : thrust(0) {}
    DroneAltOutputType(double thrust_val) : thrust(thrust_val) {}
};

class DroneAltController {
private:
    std::unique_ptr<DronePidControl> pos_control;
    std::unique_ptr<DronePidControl> spd_control;

    double delta_time;
    double mass;
    double gravity;
    double throttle_gain;

    double max_power;
    double max_spd;
    double simulation_time = 0;
    double control_cycle;

    DroneAltOutputType prev_out = {};

public:
    DroneAltController(const HakoControllerParamLoader& loader) {
        delta_time = loader.getParameter("SIMULATION_DELTA_TIME");
        control_cycle = loader.getParameter("PID_ALT_CONTROL_CYCLE");
        max_power = loader.getParameter("PID_ALT_MAX_POWER");
        max_spd = loader.getParameter("PID_ALT_MAX_SPD");
        throttle_gain = loader.getParameter("PID_ALT_THROTTLE_GAIN");
        mass = loader.getParameter("MASS");
        gravity = loader.getParameter("GRAVITY");
        pos_control = std::make_unique<DronePidControl>(
            loader.getParameter("PID_ALT_Kp"), 
            loader.getParameter("PID_ALT_Ki"), 
            loader.getParameter("PID_ALT_Kd"), 
            0, delta_time);
        spd_control = std::make_unique<DronePidControl>(
            loader.getParameter("PID_ALT_SPD_Kp"), 
            loader.getParameter("PID_ALT_SPD_Ki"), 
            loader.getParameter("PID_ALT_SPD_Kd"), 
            0, delta_time);
    }
    ~DroneAltController() {}
    DroneAltOutputType run(DroneALtInputType &in)
    {
        DroneAltOutputType out = prev_out;
        if (simulation_time >= control_cycle) {
            simulation_time = 0;
            /*
             * speed control
             */
            double target_spd = pos_control->calculate(in.target_altitude, in.pos.z);
            target_spd = flight_controller_get_limit_value(target_spd, 0, -max_spd, max_spd);
            /*
             * position control
             */
            double throttle_power = spd_control->calculate(target_spd, in.spd.w);
            throttle_power = flight_controller_get_limit_value(throttle_power, 0, -max_power, max_power);
            /*
             * thrust
             */
            out.thrust = (mass * gravity) + (throttle_gain * throttle_power);
        }
        simulation_time += delta_time;
        return out;
    }
};

#endif /* _DRONE_ALT_CONTROLLER_HPP_ */
