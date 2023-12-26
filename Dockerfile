ARG IMAGE=ubuntu:22.04
FROM ${IMAGE}
ARG IMAGE
RUN echo ${IMAGE}

ENV DEBIAN_FRONTEND="noninteractive"

# be able to source files
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

RUN apt-get update -yqq
RUN apt-get upgrade -yqq
RUN apt-get install -yqq apt-utils

# apt installs
RUN apt-get install -yqq git unzip wget libgtest-dev
RUN apt-get install -yqq libboost-dev libb64-dev libeigen3-dev libfmt-dev libgmock-dev python-is-python3 python3-venv python3-numpy python3-vcstools

# apt ros installs
RUN apt-get install -yqq ros-*
RUN apt-get install -yqq catkin-lint
# RUN apt-get install -yqq python3-catkin-pkg python3-rosdep2 python3-rospkg python3-wstool

ENV DEST=/other/install
RUN mkdir $DEST -p
ENV SRC=/other/src
RUN mkdir $SRC -p

WORKDIR $SRC
RUN git clone https://github.com/dirk-thomas/vcstool.git
WORKDIR $SRC/vcstool
RUN python3 setup.py install --prefix=$DEST --record install_manifest.txt --single-version-externally-managed

WORKDIR $SRC
RUN git clone https://github.com/osrf/osrf_pycommon.git
WORKDIR $SRC/osrf_pycommon
RUN ls -l
RUN python3 setup.py install --prefix=$DEST --record install_manifest.txt --single-version-externally-managed

WORKDIR $SRC
RUN git clone https://github.com/catkin/catkin_tools.git
WORKDIR $SRC/catkin_tools
RUN python3 setup.py install --prefix=$DEST --record install_manifest.txt --single-version-externally-managed

WORKDIR $SRC
RUN python --version | awk  '{print $2}' | cut -d'.' -f1
RUN python --version | awk  '{print $2}' | cut -d'.' -f2
# TODO(lucasw) these aren't working
# RUN export PYTHON_MAJOR_VERSION=`python --version | awk  '{print $2}' | cut -d'.' -f1`
# RUN export PYTHON_MINOR_VERSION=`python --version | awk  '{print $2}' | cut -d'.' -f2`
# RUN PYTHON_MINOR_VERSION=`python --version | awk  '{print $2}' | cut -d'.' -f2`
ARG PYTHON_MAJOR_VERSION=3
ARG PYTHON_MINOR_VERSION=10
ENV OPT_PYTHONPATH=$DEST/lib/python$PYTHON_MAJOR_VERSION.$PYTHON_MINOR_VERSION/site-packages/
RUN echo $PYTHONPATH
ENV PYTHONPATH=$OPT_PYTHONPATH
RUN echo $PYTHONPATH

ENV PATH=$DEST/bin:$PATH

# get packages and build
ENV WS=/base_catkin_ws/src
RUN mkdir $WS -p
WORKDIR $WS
COPY . $WS

# ENV ROS_DISTRO="noetic"
RUN echo $CMAKE_PREFIX_PATH

WORKDIR $WS/..
RUN catkin config --cmake-args -DCMAKE_BUILD_TYPE=Release -Wno-deprecated
RUN catkin build -j1 roscpp
RUN catkin build -j1 test_roscpp --no-deps --catkin-make-args run_tests
RUN catkin_test_results --all build/test_roscpp | grep -v "Skipping"
RUN catkin build -j1
RUN catkin build -j1 --catkin-make-args run_tests
RUN catkin_test_results --all | grep -v "Skipping"

# make 'source' work
SHELL ["/bin/bash", "-c"]
RUN source devel/setup.sh && rospack list
