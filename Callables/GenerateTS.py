import sys, os
import argparse
import numpy as np

# this add to path eBCSgen home dir, so it can be called from anywhere
sys.path.append(os.path.split(sys.path[0])[0])

from Parsing.ParseBCSL import Parser, load_TS_from_json
from Errors.ModelParsingError import ModelParsingError
from Errors.UnspecifiedParsingError import UnspecifiedParsingError
from Errors.RatesNotSpecifiedError import RatesNotSpecifiedError

"""
usage: GenerateTS.py [-h] --model MODEL --output OUTPUT
                     [--transition_file TRANSITION_FILE] [--max_time MAX_TIME]
                     [--max_size MAX_SIZE] [--bound BOUND]

Transition system generating

required arguments:
  --model MODEL
  --output OUTPUT

optional arguments:
  --transition_file TRANSITION_FILE
  --max_time MAX_TIME
  --max_size MAX_SIZE
  --bound BOUND
"""

args_parser = argparse.ArgumentParser(description='Transition system generating')

args_parser._action_groups.pop()
required = args_parser.add_argument_group('required arguments')
optional = args_parser.add_argument_group('optional arguments')

required.add_argument('--model', type=str, required=True)
required.add_argument('--output', type=str, required=True)

optional.add_argument('--transition_file')
optional.add_argument('--max_time', type=float, default=np.inf)
optional.add_argument('--max_size', type=float, default=np.inf)
optional.add_argument('--bound', type=int, default=None)

args = args_parser.parse_args()

if args.transition_file and args.transition_file != 'None':
    ts = load_TS_from_json(args.transition_file)
else:
    ts = None

model_parser = Parser("model")
model_str = open(args.model, "r").read()

model = model_parser.parse(model_str)
if model.success:
    if not model.data.all_rates:
        raise RatesNotSpecifiedError

    vm = model.data.to_vector_model(args.bound)
    ts = vm.generate_transition_system(ts, args.max_time, args.max_size)
    ts.save_to_json(args.output)
else:
    if "error" in model.data:
        raise UnspecifiedParsingError(model.data["error"])
    raise ModelParsingError(model.data, model_str)
