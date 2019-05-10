import os


class Binder:
    def __init__(self, input_names: iter = tuple(), output_names: iter = tuple()):
        self._input = tuple(input_names)
        self._output = tuple(output_names)
        self._input_dict = dict()
        self._output_dict = dict()
        for k in self._input:
            self._input_dict[k] = None
        for k in self._output:
            self._output_dict[k] = None
    
    def connect(self, input_name, output_name):
        self.disconnect(output_name=output_name)
        self._input_dict[input_name] = output_name
        self.disconnect(input_name=input_name)
        self._output_dict[output_name] = input_name
    
    def disconnect(self, input_name=None, output_name=None):
        if input_name and output_name:
            self._input_dict[input_name] = None
            self._output_dict[output_name] = None
        elif input_name and output_name is None:
            for k in self._output_dict.keys():
                if self._output_dict[k] == input_name:
                    self._output_dict[k] = None
        elif input_name is None and output_name:
            for k in self._input_dict.keys():
                if self._input_dict[k] == output_name:
                    self._input_dict[k] = None
        else:
            for k in self._input_dict.keys():
                self._input_dict[k] = None
            for k in self._output_dict.keys():
                self._output_dict[k] = None
    
    def infer(self, input_name):
        return self._input_dict[input_name]
    
    def refer(self, output_name):
        return self._output_dict[output_name]
    
    @property
    def input_names(self):
        self._input = tuple(self._input_dict.keys())
        return self._input
    
    @input_names.setter
    def input_names(self, input_names: iter = tuple()):
        self.disconnect()
        self._input = tuple(input_names)
        self._input_dict.clear()
        for k in self._input:
            self._input_dict[k] = None
    
    @property
    def output_names(self):
        self._output = tuple(self._output_dict.keys())
        return self._output
    
    @output_names.setter
    def output_names(self, output_names: iter = tuple()):
        self.disconnect()
        self._output = tuple(output_names)
        self._output_dict.clear()
        for k in self._output:
            self._output_dict[k] = None
    
    def __repr__(self):
        result = os.linesep.join((str(self.input_names), str(self.output_names)))
        for k, v in self._input_dict.items():
            if v:
                result += os.linesep
                result += '%s <--> %s' % (k, v)
        return result
