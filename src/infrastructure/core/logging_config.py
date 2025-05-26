import logging
import re
from rich.logging import RichHandler
from infrastructure.core.settings import settings # To access api_debug for log level

# --- Structured Logging Configuration with Rich & Regex --- 

# Each key (e.g., "API", "DOMAIN_MODELS") will become part of a unique tag like "[LOG_STYLE:API]"
# The patterns are regex strings to match logger names (e.g., record.name)
LAYER_STYLES_CONFIG = {
    "API": {
        "patterns": [r"^src\.api(?:\..+)?"], # Matches src.api and any submodule
        "style": "bold sky_blue1"
    },
    "APPLICATION": {
        "patterns": [r"^src\.application(?:\..+)?"], # Matches src.application and any submodule
        "style": "bold bright_green"
    },
    "DOMAIN_MODELS": {
        # Matches loggers like src.domain.<any_bc>.models.<module>, src.domain.core.models.<module>
        # <any_bc> can be customers, orders, products, etc.
        "patterns": [r"^src\.domain\.(?:[^.]+|core)\.models(?:\..+)?"],
        "style": "orange3"
    },
    "DOMAIN_EVENTS_INTERNAL": {
        # Matches loggers in src.domain.<any_bc>.events.* and src.domain.core.events.* 
        "patterns": [r"^src\.domain\.(?:[^.]+|core)\.events(?:\..+)?"],
        "style": "gold3"
    },
    "INTEGRATION_CONTRACTS": {
        "patterns": [r"^src\.integration_contracts(?:\..+)?"],
        "style": "bold magenta"
    },
    "INFRA_EVENT_PUBLISHING": {
        # Covers mappers and publishers for integration events for specific or all BCs
        # This one is a bit trickier to make fully generic if styles per BC were ever needed without new top-level keys.
        # Assuming for now a common style for all event publishing/mapping under infrastructure.<bc>.event_...
        "patterns": [
            r"^src\.infrastructure\.(?:[^.]+)\.event_(?:publishing|mapping)(?:\..+)?"
        ],
        "style": "deep_pink2"
    },
    "INFRA_CORE_EVENT_SYSTEM": {
        "patterns": [r"^src\.infrastructure\.core\.events(?:\..+)?"], # Dispatchers, registry, bootstrap
        "style": "grey62"
    },
    "INFRA_PERSISTENCE": {
        # Matches src.infrastructure.<any_bc>.persistence.* and src.infrastructure.core.persistence.*
        "patterns": [
            r"^src\.infrastructure\.(?:[^.]+|core)\.persistence(?:\..+)?"
        ],
        "style": "steel_blue3"
    },
    "INFRA_SERVICES_EXTERNAL": {
        # Example: src.infrastructure.customers.services. If you add src.infrastructure.products.services, it will be caught.
        "patterns": [r"^src\.infrastructure\.(?:[^.]+)\.services(?:\..+)?"], 
        "style": "light_slate_grey"
    },
    "MAIN_CONFIG_SETUP": {
        "patterns": [r"^src\.main(?:\..+)?", r"^src\.infrastructure\.core\.settings(?:\..+)?"],
        "style": "grey42"
    },
    "TESTS": { 
        "patterns": [r"^src\.tests(?:\..+)?", r"^tests(?:\..+)?"], 
        "style": "italic #008080"
    }
    # Add a default catch-all if desired, though RichHandler has its own defaults
    # "DEFAULT": {
    #     "patterns": [r".*"], # Matches any logger name if no other rule matched (due to filter logic)
    #     "style": "default" # Rich's default style
    # }
}

STYLE_TAG_PREFIX = "[LOG_STYLE:\""
STYLE_TAG_SUFFIX = "\"]"

class RegexStyleTagFilter(logging.Filter):
    def __init__(self, layer_styles_config):
        super().__init__()
        self.layer_styles_config = layer_styles_config
        self.compiled_patterns = []
        # Sort layer keys to ensure that more specific regex patterns are tried first if there is potential for overlap
        # This is a simple sort, for very complex regex overlaps, more sophisticated ordering might be needed.
        # However, with distinct top-level keys, it mainly helps if some patterns are subsets of others accidentally.
        sorted_layer_keys = sorted(layer_styles_config.keys(), key=lambda k: sum(len(p) for p in layer_styles_config[k]["patterns"]), reverse=True)

        for layer_key in sorted_layer_keys:
            config = self.layer_styles_config[layer_key]
            style_to_apply = config["style"]
            for pattern_str in config["patterns"]:
                try:
                    self.compiled_patterns.append((re.compile(pattern_str), style_to_apply))
                except re.error as e:
                    print(f"Error compiling regex '{pattern_str}' for {layer_key}: {e}")

    def filter(self, record):
        if not hasattr(record, "original_msg"): 
            record.original_msg = record.msg
        else:
            record.msg = record.original_msg 

        if not isinstance(record.msg, str):
            record.msg = str(record.msg)

        for compiled_regex, style_to_apply in self.compiled_patterns:
            if compiled_regex.fullmatch(record.name): 
                # Apply style as Rich markup, ensuring to use original_msg to avoid re-wrapping
                record.msg = f"[{style_to_apply}]{record.original_msg}[/]"
                break 
        return True 

def setup_logging():
    """Configures the root logger with RichHandler and RegexStyleTagFilter."""
    
    # Create the custom filter
    regex_filter = RegexStyleTagFilter(LAYER_STYLES_CONFIG)

    # Configure Root Logger
    root_logger = logging.getLogger()
    
    # Clear any existing handlers to avoid duplicate logs or formatting conflicts
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        handler.close()

    rich_handler_instance = RichHandler(
        rich_tracebacks=True,
        show_path=False, # Logger name (record.name) is used by our filter, not raw path
        markup=True,     # Allows Rich markup in the original log messages too
        log_time_format="[%X]", # Example: [10:34:12]
        show_level=True
    )
    
    # Add our custom filter to the handler, so it modifies the record before Rich formats it
    # Alternatively, add filter to root_logger, but adding to handler is also fine.
    rich_handler_instance.addFilter(regex_filter)

    root_logger.addHandler(rich_handler_instance)
    root_logger.setLevel(logging.DEBUG if settings.api_debug else logging.INFO)

    # Optional: Silence very verbose loggers from libraries if needed
    # logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    # logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

    # Test log to verify setup during startup (optional)
    # logging.getLogger("src.infrastructure.core.logging_config").info("Rich logging configured with regex styling.") 