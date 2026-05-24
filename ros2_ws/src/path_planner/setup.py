from setuptools import setup


package_name = "path_planner"


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
    description="UGV path planner package.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "planner_node = path_planner.planner_node:main",
        ]
    },
)

