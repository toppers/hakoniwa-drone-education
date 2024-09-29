#ifndef _DRONE_HEADING_CONTROLLER_HPP_
#define _DRONE_HEADING_CONTROLLER_HPP_

#include "drone_pid_control.hpp"
#include "flight_controller_types.hpp"
#include "hako_controller_param_loader.hpp"

struct DroneHeadingControlInputType {
    FlightControllerInputEulerType euler;
    double target_angle_deg;
    DroneHeadingControlInputType() : target_angle_deg(0) {}
    DroneHeadingControlInputType(FlightControllerInputEulerType e, double t_e) : euler(e), target_angle_deg(t_e) {}    
};

struct DroneHeadingControlOutputType {
    double angular_rate_r;
    DroneHeadingControlOutputType() : angular_rate_r(0) {}
    DroneHeadingControlOutputType(double angular_rate_r_val) : angular_rate_r(angular_rate_r_val) {}
};

class DroneHeadingController {
private:
    double delta_time;
    double pid_param_max_yaw_rate;
    std::unique_ptr<DronePidControl> heading_control;
    DroneHeadingControlOutputType prev_out = {};
    double simulation_time = 0;

    double normalize_angle(double angle) {
        // Normalize angle to be within the range [0, 360)
        angle = std::fmod(angle, 360.0);
        if (angle < 0) {
            angle += 360.0;
        }
        return angle;
    }

    double shortest_angle(double current, double target) {
        double diff = normalize_angle(target - current);
        if (diff > 180.0) {
            diff -= 360.0;
        } else if (diff < -180.0) {
            diff += 360.0;
        }
        return diff;
    }

public:
    double head_control_cycle;
    DroneHeadingController(const HakoControllerParamLoader& loader)
    {
        delta_time = loader.getParameter("SIMULATION_DELTA_TIME");
        head_control_cycle = loader.getParameter("HEAD_CONTROL_CYCLE");
        pid_param_max_yaw_rate = loader.getParameter("PID_PARAM_MAX_YAW_RATE");
        heading_control = std::make_unique<DronePidControl>(
            loader.getParameter("PID_YAW_Kp"), 
            loader.getParameter("PID_YAW_Ki"), 
            loader.getParameter("PID_YAW_Kd"), 
            0, delta_time);
    }

    virtual ~DroneHeadingController() {}

    DroneHeadingControlOutputType run(DroneHeadingControlInputType& in) {
        DroneHeadingControlOutputType out = prev_out;
        if (simulation_time >= head_control_cycle) {
            simulation_time = 0;
            double current_angle = normalize_angle(RADIAN2DEGREE(in.euler.z));
            double target_angle = normalize_angle(in.target_angle_deg);
            // Calculate the shortest path to the target angle
            double shortest_diff = shortest_angle(current_angle, target_angle);

            out.angular_rate_r = heading_control->calculate(current_angle + shortest_diff, current_angle);
            out.angular_rate_r = flight_controller_get_limit_value(out.angular_rate_r, 0, -pid_param_max_yaw_rate, pid_param_max_yaw_rate);
        }
        simulation_time += delta_time;
        return out;
    }
};

#endif /* _DRONE_HEADING_CONTROLLER_HPP_ */
