import tempfile
import shutil
import logging

def before_scenario(context, scenario):
    context.temp_dir = tempfile.mkdtemp()
    context.config.setup_logging()
    
def after_scenario(context, scenario):
    shutil.rmtree(context.tempdir)