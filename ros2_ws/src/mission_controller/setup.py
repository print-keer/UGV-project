from setuptools import setup


package_name = "mission_controller"


setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", ["launch/person1_stack.launch.py"]),
        (f"share/{package_name}/launch", ["launch/person1_visualization.launch.py"]),
        (f"share/{package_name}/launch", ["launch/person1_hardware_sensors.launch.py"]),
        (f"share/{package_name}/launch", ["launch/person1_observe.launch.py"]),
        (f"share/{package_name}/rviz", ["rviz/person1_navigation.rviz"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="UGV Team",
    maintainer_email="maintainer@example.com",
    description="UGV mission controller package.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "mission_demo = mission_controller.demo:main",
            "mission_controller_node = mission_controller.mission_controller_node:main",
            "visualizer_node = mission_controller.visualizer_node:main",
            "monitor_node = mission_controller.monitor_node:main",
        ]
    },
)
