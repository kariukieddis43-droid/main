from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

app_path = Path(__file__).with_name('amo prof.py')
spec = spec_from_file_location('amo_prof_app', app_path)
if spec is None or spec.loader is None:
    raise RuntimeError(f'Could not load Flask app from {app_path}')

module = module_from_spec(spec)
spec.loader.exec_module(module)
app = module.app
