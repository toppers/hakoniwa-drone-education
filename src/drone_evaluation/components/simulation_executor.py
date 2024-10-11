#!/usr/bin/python
# -*- coding: utf-8 -*-

import hakosim
import hakopy
import pdu_info
import hako_pdu
import os
import json
from input_param_loader import InputParamLoader
from drone_executor_factory import DroneExecutorFactory
from impl.logger import Logger
from signal_factory import SignalFactory
from isignal_generator import ISignalGenerator

class SimulationExecutor:
    def __init__(self, drone_config_path, pdu_config_path, evaluation_config_path):
        self.asset_name = 'SimulationExecutor'

        # config
        self.drone_config_params = self._load_json(drone_config_path)
        self.pdu_config_path = pdu_config_path
        self.loader = InputParamLoader(evaluation_config_path)
        self.evaluation_params = self.loader.load_params()

        # drone api
        client = hakosim.MultirotorClient(self.pdu_config_path)
        client.default_drone_name = self.drone_config_params['name']
        hako_binary_path = os.getenv('HAKO_BINARY_PATH', '/usr/local/lib/hakoniwa/hako_binary/offset')
        client.pdu_manager = hako_pdu.HakoPduManager(hako_binary_path, self.pdu_config_path)
        client.enableApiControl(True)
        client.armDisarm(True)
        self.client = client

        # drone executor
        self.logger = Logger(filename='out.csv')
        exec_factory = DroneExecutorFactory(self.loader)
        self.drone_executor = exec_factory.create_executor(self.client, self.logger)

        # signal
        self.signal_factory = SignalFactory(self.evaluation_params)


    def initialize(self, my_callback):
        delta_time_usec = int(self.drone_config_params['simulation']['timeStep'] * 1000000)
        self.delta_time_usec = delta_time_usec
        self.delta_time_sec = self.drone_config_params['simulation']['timeStep']
        print("delta_time_usec:", delta_time_usec)

        # connect to the HakoSim simulator
        ret = hakopy.asset_register(self.asset_name, self.pdu_config_path, my_callback, delta_time_usec, hakopy.HAKO_ASSET_MODEL_PLANT)
        if ret == False:
            print(f"ERROR: hako_asset_register() returns {ret}.")
            return False
        return True

    def create_pdu(self):
        robot_name = self.client.default_drone_name
        hako_binary_path = os.getenv('HAKO_BINARY_PATH', '/usr/local/lib/hakoniwa/hako_binary/offset')
        pdu_manager = hako_pdu.HakoPduManager(hako_binary_path, self.pdu_config_path)

        pdu_channels = [
            pdu_info.HAKO_AVATOR_CHANNLE_ID_COLLISION,
            pdu_info.HAKO_AVATOR_CHANNEL_ID_DISTURB,
            pdu_info.HAKO_AVATOR_CHANNEL_ID_CAMERA_DATA,
            pdu_info.HAKO_AVATOR_CHANNEL_ID_CAMERA_INFO,
            pdu_info.HAKO_AVATOR_CHANNEL_ID_LIDAR_DATA,
            pdu_info.HAKO_AVATOR_CHANNEL_ID_LIDAR_POS,
            pdu_info.HAKO_AVATOR_CHANNEL_ID_STAT_MAG,
        ]

        for channel in pdu_channels:
            pdu = pdu_manager.get_pdu(robot_name, channel)
            _ = pdu.get()
            pdu.write()

    def start(self):
        ret = hakopy.start()
        return ret

    def _load_json(self, filepath):
        try:
            with open(filepath, 'r') as file:
                params = json.load(file)
                return params
        except FileNotFoundError:
            raise FileNotFoundError(f"The file at {filepath} was not found.")
        except json.JSONDecodeError:
            raise ValueError(f"The file at {filepath} is not a valid JSON file.")

    def run_duration(self, signal_generators: list[ISignalGenerator], duration_sec: float):
        start_time_usec = hakopy.simulation_time()
        duration_usec = int(duration_sec * 1000000)
        end_time_usec = start_time_usec + duration_usec
        current_time_usec = start_time_usec

        # create signal
        signals_sequence = []
        for signal_generator in signal_generators:
            signal_sequence = signal_generator.generate_signal(self.delta_time_sec, duration_sec)
            signals_sequence.append(signal_sequence)

        # Check if all signal sequences have the same length
        sequence_len = len(signals_sequence[0])
        print("INFO sequence_len: ", sequence_len)
        if not all(len(seq) == sequence_len for seq in signals_sequence):
            raise ValueError("All signal sequences must have the same length.")

        index = 0
        while current_time_usec < end_time_usec:
            signals = [signal_sequence[index] for signal_sequence in signals_sequence]
            self.drone_executor.run(current_time_usec, signals)
            hakopy.usleep(self.delta_time_usec)
            current_time_usec = hakopy.simulation_time()
            index = (index + 1) % sequence_len

    def run(self):
        # takeoff
        print("INFO: start takeoff")
        self.drone_executor.takeoff()

        # do simulation
        for sigina_input_timing in self.evaluation_params['simulation']['signal_input_timings']:
            signal_name = sigina_input_timing['name']
            signal_duration_sec = sigina_input_timing['duration_sec']
            print("INFO: signal_name: ", signal_name)
            print("INFO: signal_duration_sec: ", signal_duration_sec)
            signal_generators = self.signal_factory.create_signal_generator(signal_name)
            print("INFO signal_generators num: ", len(signal_generators))
            self.run_duration(signal_generators, signal_duration_sec)

