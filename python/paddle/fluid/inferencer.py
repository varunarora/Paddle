#   Copyright (c) 2018 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import core

import executor
import framework
import io
import unique_name
from trainer import check_and_get_place

__all__ = ['Inferencer', ]


class Inferencer(object):
    def __init__(self, infer_func, param_path, place=None):
        """
        :param infer_func: a function that will return predict Variable
        :param param_path: the path where the inference model is saved by fluid.io.save_params
        :param place: place to do the inference
        """
        self.param_path = param_path
        self.scope = core.Scope()

        self.inference_program = framework.Program()
        with framework.program_guard(self.inference_program):
            with unique_name.guard():
                self.predict_var = infer_func()

        self.exe = executor.Executor(check_and_get_place(place))
        with executor.scope_guard(self.scope):
            # load params from param_path into scope
            io.load_params(self.exe, param_path, self.inference_program)

    def infer(self, inputs, return_numpy=True):
        """
        :param inputs: a map of {"input_name": input_var} that will be feed into the inference program
        to get the predict value
        :param return_numpy: if return numpy value for row tensor
        :return: the predict value of the inference model
        """
        if not isinstance(inputs, dict):
            raise ValueError(
                "inputs should be a map of {'input_name': input_var}")

        with executor.scope_guard(self.scope):
            results = self.exe.run(self.inference_program,
                                   feed=inputs,
                                   fetch_list=[self.predict_var],
                                   return_numpy=return_numpy)

        return results
