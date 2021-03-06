import sys, os
import argparse

# this add to path eBCSgen home dir, so it can be called from anywhere
sys.path.append(os.path.split(sys.path[0])[0])

from Parsing.ParseBCSL import Parser
from Errors.ModelParsingError import ModelParsingError
from Errors.UnspecifiedParsingError import UnspecifiedParsingError
from Errors.InvalidInputError import InvalidInputError
from Errors.RatesNotSpecifiedError import RatesNotSpecifiedError

"""
usage: Simulation.py [-h] --model MODEL --output OUTPUT --deterministic
                     DETERMINISTIC --runs RUNS --max_time MAX_TIME --volume
                     VOLUME --step STEP

Simulation

required arguments:
  --model MODEL
  --output OUTPUT
  --deterministic DETERMINISTIC
  --runs RUNS
  --max_time MAX_TIME
  --volume VOLUME
  --step STEP
"""

args_parser = argparse.ArgumentParser(description='Simulation')

args_parser._action_groups.pop()
required = args_parser.add_argument_group('required arguments')

required.add_argument('--model', type=str, required=True)
required.add_argument('--output', type=str, required=True)
required.add_argument('--deterministic', required=True)
required.add_argument('--runs', type=int, required=True)
required.add_argument('--max_time', type=float, required=True)
required.add_argument('--volume', type=float, required=True)
required.add_argument('--step', type=float, required=True)

args = args_parser.parse_args()

model_parser = Parser("model")
model_str = open(args.model, "r").read()

model = model_parser.parse(model_str)

if model.success:
    if len(model.data.params) != 0:
        raise InvalidInputError("Provided model is parametrised - simulation cannot be executed.")
    if not model.data.all_rates:
        raise RatesNotSpecifiedError

    vm = model.data.to_vector_model()
    if eval(args.deterministic):
        df = vm.deterministic_simulation(args.max_time, args.volume, args.step)
    else:
        df = vm.stochastic_simulation(args.max_time, args.runs)

    df.to_csv(args.output, index=None, header=True)
else:
    if "error" in model.data:
        raise UnspecifiedParsingError(model.data["error"])
    raise ModelParsingError(model.data, model_str)
