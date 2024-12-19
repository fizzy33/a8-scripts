from model import ChangeTheWorldServices, LogArchiver, YearMonthDayDirs, YearMonthDayNestedDirs, PostgresLogArchiver, DryRunServices, Process, CleanerUpper
from util import Path, logger
from datetime import timedelta
import argparse
from pyhocon import ConfigFactory


services = DryRunServices()

services = ChangeTheWorldServices()

CLEANUP_CLASS_MAP = {
    "PGLogArchive": PostgresLogArchiver,
    "LogArchive": LogArchiver,
    "YMDNestClean": YearMonthDayNestedDirs,
    "YMDClean": YearMonthDayDirs,
}

def parse_value(value):
    # Limits Python functionalities that can be used in the config
    allowed_builtins = {
        "str": str,
        "timedelta": timedelta,
        "Path": Path,
    }
    
    safe_globals = {
        "__builtins__": None,
        **allowed_builtins,
    }

    try:
        return eval(value, safe_globals, {})
    except Exception as e:
        raise ValueError(f"Failed to evaluate value '{value}': {e}")

def initialize_cleanup_task(task) -> CleanerUpper:
    """
    Initializes a cleanup task by dynamically determining its class
    and evaluating its parameters.
    """
    task_type = task.get("type")
    task_args = task.get("args")
    if not task_type or task_type not in CLEANUP_CLASS_MAP:
        raise ValueError(f"Unknown or missing cleanup type: {task_type}")
    
    # Dynamically initialize the CleanUp class
    init_args = {}
    for key, value in task_args.items():
        if key != "type":
            init_args[key] = parse_value(value)
    
    cleanup_class = CLEANUP_CLASS_MAP[task_type]
    return cleanup_class(**init_args)

def process_cleanup_tasks(json_obj) -> list[CleanerUpper]:
    """
    Processes the cleanUp.tasks from a JSON object and initializes the tasks.
    """
    cleanup_tasks = json_obj.get("cleanUp", {}).get("tasks", [])
    if not isinstance(cleanup_tasks, list):
        raise ValueError("'cleanUp.tasks' must be a list.")
    

    initialized_tasks = []
    for task in cleanup_tasks:
        try:
            initialized_task = initialize_cleanup_task(task)
            initialized_tasks.append(initialized_task)
        except Exception as e:
            logger.error(f"Failed to initialize task {task}: {e}. Stopping Python Process!")
            return

    return initialized_tasks


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process cleanup tasks from a HOCON file.")
    parser.add_argument("hocon_path", help="Path to the HOCON file containing cleanup tasks.")
    args = parser.parse_args()

    try:
        hocon_config = ConfigFactory.parse_file(args.hocon_path)
        parsed_tasks = process_cleanup_tasks(hocon_config)
        for task in parsed_tasks:
            task.run_cleanup()
    except Exception as e:
        logger.error(f"Error processing tasks: {e}")

