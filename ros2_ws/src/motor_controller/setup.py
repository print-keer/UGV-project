from setuptools import setup


package_name = "motor_controller"


setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="UGV Team",
    maintainer_email="maintainer@example.com",
    description="UGV motor controller stub package.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "motor_controller_node = motor_controller.motor_controller_node:main",
        ]
    },
)
