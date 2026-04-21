import logging
import asyncio
import traceback


# --- Logging Setup ---
class LoopIdFilter(logging.Filter):
    def filter(self, record):
        try:
            record.loop_id = id(asyncio.get_running_loop())
        except RuntimeError:
            record.loop_id = "no-loop"
        return True


def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - [%(loop_id)s] %(message)s",
    )
    logger = logging.getLogger("llm_engine_search")

    # Remove existing filters/handlers if any to prevent duplication
    for f in logger.filters[:]:
        logger.removeFilter(f)

    logger.addFilter(LoopIdFilter())
    return logger


logger = setup_logger()


def log_print(level, message="", exception=None, details=None):
    """Helper function for structured logging natively via logging module"""
    log_func = logger.info
    if level.upper() == "ERROR":
        log_func = logger.error
    elif level.upper() == "WARNING":
        log_func = logger.warning

    formatted_msg = message
    if details:
        formatted_msg += f". Details: {details}"

    if exception:
        log_func(
            f"{formatted_msg}. Exception: {exception}\nTraceback: {traceback.format_exc()}"
        )
    else:
        log_func(formatted_msg)
