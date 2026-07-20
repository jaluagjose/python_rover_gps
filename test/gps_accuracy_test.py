#!/usr/bin/env python3

import csv
import math
import statistics
from datetime import datetime
from pathlib import Path

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix
from sensor_msgs.msg import NavSatStatus


# ============================================================
# TEST SETTINGS
# ============================================================

SAMPLE_TARGET = 300
OUTPUT_FOLDER = Path("gps_logs")

# Reject coordinates outside normal geographic limits.
MIN_LATITUDE = -90.0
MAX_LATITUDE = 90.0
MIN_LONGITUDE = -180.0
MAX_LONGITUDE = 180.0


def haversine_distance_m(lat1, lon1, lat2, lon2):
    """Return great-circle distance between two GPS coordinates in meters."""

    earth_radius_m = 6_371_000.0

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)

    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2.0) ** 2
        + math.cos(lat1_rad)
        * math.cos(lat2_rad)
        * math.sin(delta_lon / 2.0) ** 2
    )

    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return earth_radius_m * c


class GPSAccuracyTest(Node):

    def __init__(self):
        super().__init__("gps_accuracy_test")

        OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_path = OUTPUT_FOLDER / f"gps_accuracy_{timestamp}.csv"

        self.samples = []
        self.rejected_samples = 0
        self.finished = False

        self.subscription = self.create_subscription(
            NavSatFix,
            "/fix",
            self.gps_callback,
            10
        )

        print("=" * 60)
        print("GPS ACCURACY TEST")
        print("=" * 60)
        print("Keep the rover completely stationary.")
        print(f"Collecting {SAMPLE_TARGET} valid GPS samples.")
        print(f"Output file: {self.output_path}")
        print("=" * 60)

    def gps_callback(self, msg):
        if self.finished:
            return

        if not self.is_valid_fix(msg):
            self.rejected_samples += 1

            print(
                f"\rWaiting for valid GPS... "
                f"Rejected: {self.rejected_samples}",
                end="",
                flush=True
            )
            return

        sample = {
            "ros_time_sec": msg.header.stamp.sec,
            "ros_time_nanosec": msg.header.stamp.nanosec,
            "latitude": msg.latitude,
            "longitude": msg.longitude,
            "altitude": msg.altitude,
            "status": msg.status.status,
            "service": msg.status.service,
            "covariance_type": msg.position_covariance_type,
            "covariance_x": msg.position_covariance[0],
            "covariance_y": msg.position_covariance[4],
            "covariance_z": msg.position_covariance[8],
        }

        self.samples.append(sample)

        print(
            f"\rValid samples: {len(self.samples)}/{SAMPLE_TARGET} "
            f"| Rejected: {self.rejected_samples} "
            f"| Lat: {msg.latitude:.8f} "
            f"| Lon: {msg.longitude:.8f}",
            end="",
            flush=True
        )

        if len(self.samples) >= SAMPLE_TARGET:
            self.finished = True
            print()
            self.save_and_analyze()

    @staticmethod
    def is_valid_fix(msg):
        if not math.isfinite(msg.latitude):
            return False

        if not math.isfinite(msg.longitude):
            return False

        if not (
            MIN_LATITUDE <= msg.latitude <= MAX_LATITUDE
            and MIN_LONGITUDE <= msg.longitude <= MAX_LONGITUDE
        ):
            return False

        # STATUS_NO_FIX is -1.
        if msg.status.status == NavSatStatus.STATUS_NO_FIX:
            return False

        return True

    def save_and_analyze(self):
        if not self.samples:
            print("No valid samples were collected.")
            return

        latitudes = [sample["latitude"] for sample in self.samples]
        longitudes = [sample["longitude"] for sample in self.samples]

        mean_latitude = statistics.fmean(latitudes)
        mean_longitude = statistics.fmean(longitudes)

        errors_m = [
            haversine_distance_m(
                sample["latitude"],
                sample["longitude"],
                mean_latitude,
                mean_longitude
            )
            for sample in self.samples
        ]

        mean_error_m = statistics.fmean(errors_m)
        median_error_m = statistics.median(errors_m)
        maximum_error_m = max(errors_m)

        if len(errors_m) >= 2:
            standard_deviation_m = statistics.stdev(errors_m)
        else:
            standard_deviation_m = 0.0

        sorted_errors = sorted(errors_m)

        percentile_95_index = min(
            len(sorted_errors) - 1,
            math.ceil(0.95 * len(sorted_errors)) - 1
        )

        percentile_95_m = sorted_errors[percentile_95_index]

        with self.output_path.open(
            "w",
            newline="",
            encoding="utf-8"
        ) as csv_file:

            fieldnames = list(self.samples[0].keys()) + [
                "distance_from_average_m"
            ]

            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

            for sample, error_m in zip(self.samples, errors_m):
                row = dict(sample)
                row["distance_from_average_m"] = error_m
                writer.writerow(row)

        print()
        print("=" * 60)
        print("GPS ACCURACY RESULTS")
        print("=" * 60)
        print(f"Valid samples       : {len(self.samples)}")
        print(f"Rejected samples    : {self.rejected_samples}")
        print(f"Average latitude    : {mean_latitude:.8f}")
        print(f"Average longitude   : {mean_longitude:.8f}")
        print(f"Mean error          : {mean_error_m:.2f} m")
        print(f"Median error        : {median_error_m:.2f} m")
        print(f"95th percentile     : {percentile_95_m:.2f} m")
        print(f"Maximum error       : {maximum_error_m:.2f} m")
        print(f"Error std deviation : {standard_deviation_m:.2f} m")
        print(f"CSV saved to        : {self.output_path}")
        print("=" * 60)

        print()
        print("Interpretation:")
        print(
            "Use the 95th-percentile value as an initial estimate "
            "of normal stationary GPS wander."
        )


def main():
    rclpy.init()

    node = GPSAccuracyTest()

    try:
        while rclpy.ok() and not node.finished:
            rclpy.spin_once(node, timeout_sec=1.0)

    except KeyboardInterrupt:
        print("\nTest stopped by user.")

    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()