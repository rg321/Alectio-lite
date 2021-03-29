from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import os
import sys
import random
import logging
import alectiolite
from .init import init_experiment_, extract_config_
from .curate.classification import UniClassification as curate_classification
from .curate.object_detection import ObjectDetection as curate_object_detection
from .curate.object_segmentation import ObjectSegmentation as curate_object_segmentation
from .logger.logger import LoggerController, complete_loop

__all__ = [
    "backend",
    "curate",
    "proto",
    "callbacks" "init_experiment_",
    "UniClassification",
    "ObjectDetection",
    "ObjectSegmentation",
    "LoggerController",
    "complete_loop",
]


init = alectiolite.init_experiment_
experiment_config = alectiolite.extract_config_
curate_classification = alectiolite.curate_classification
curate_object_detection = alectiolite.curate_object_detection
curate_object_segmentation = alectiolite.curate_object_segmentation
alectio_logger = alectiolite.LoggerController
complete_loop = alectiolite.complete_loop
