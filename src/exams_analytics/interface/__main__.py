import asyncio
import os
import logging
import logging.config
import hypercorn.asyncio
from hypercorn.config import Config
import sys

from exams_analytics.interface.results.http_results_facade import http_results_facade
from exams_analytics.interface.scan_import.http_rest_facade import http_scan_import_quart

logger = logging.getLogger(__name__)

if os.getenv("HTTP_PORT_MARKR") is None:
    print("Environment Var: HTTP_PORT_MARKR not set")
    raise ValueError("You must define HTTP_PORT_MARKR")


def handle_exception(exc_type, exc_value, exc_traceback):
    """
    Custom exception handler.
    Logs the exception using the configured logger.
    """
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger = logging.getLogger("root")
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

async def run_http_server_task():
    config = Config()
    port = os.getenv("HTTP_PORT_MARKR","The variable exists, it's checked when the file is loaded")
    config.bind = ["0.0.0.0:"+port]
    http_scan_import_quart.register_blueprint(http_results_facade)
    http_scan_import_quart.config['EXPLAIN_TEMPLATE_LOADING'] = False
    logger.warning("ALERT!! This server is not secured with SSL!! should be added in the future!!")
    await hypercorn.asyncio.serve(http_scan_import_quart, config)

async def main():
    sys.excepthook = handle_exception
    
    logging.basicConfig()
    log_level = os.environ.get('LOGLEVEL', 'WARNING').upper()
    logging.getLogger().setLevel(log_level)

    logger.info("Starting main")

    asyncio.get_event_loop().slow_callback_duration = 0.1
    logger.info(f"Slow callback duration set to {asyncio.get_event_loop().slow_callback_duration} seconds")

    await asyncio.create_task(run_http_server_task())


if __name__ == "__main__":
    asyncio.run(main()) #, debug=True)
