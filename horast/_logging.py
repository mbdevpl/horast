"""Default logging mechanism for horast module."""

import logging
import logging.config
import os
import pathlib
import platform
import typing as t

import colorama

LOGS_PATHS = {
    'Linux': pathlib.Path('~', '.local', 'share'),
    'Darwin': pathlib.Path('~', 'Library', 'Logs'),
    'Windows': pathlib.Path('%LOCALAPPDATA%')}

LOGS_PATH = LOGS_PATHS[platform.system()].joinpath('horast')


def normalize_path(path: t.Union[pathlib.Path, str]) -> t.Union[pathlib.Path, str]:
    if isinstance(path, str):
        return os.path.expanduser(os.path.expandvars(path))
    return pathlib.Path(normalize_path(str(path)))


def logging_level_from_envvar(envvar: str, default: int = logging.WARNING) -> int:
    """Translate text envvar value into an integer corresponding to a logging level."""
    envvar_value = os.environ.get(envvar)
    if envvar_value is None:
        return default
    envvar_value = envvar_value.upper()
    if not hasattr(logging, envvar_value):
        try:
            return int(envvar_value)
        except ValueError:
            return default
    return getattr(logging, envvar_value)


colorama.init()

if not normalize_path(LOGS_PATH).is_dir():
    normalize_path(LOGS_PATH).mkdir(parents=True)

logging.config.dictConfig({
    'formatters': {
        'brief': {
            '()': 'colorlog.ColoredFormatter',
            'style': '{',
            'format': '{name} [{log_color}{levelname}{reset}] {message}'},
        'precise': {
            'style': '{',
            'format': '{asctime} {name} [{levelname}] {message}'}},
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'brief',
            'level': logging_level_from_envvar('LOGGING_LEVEL'),
            'stream': 'ext://sys.stdout'},
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'precise',
            'level': logging.NOTSET,
            'filename': normalize_path(str(LOGS_PATH.joinpath('horast.log'))),
            'maxBytes': 1 * 1024 * 1024,
            'backupCount': 10}},
    'root': {
        'handlers': ['console', 'file'],
        'level': logging.NOTSET},
    'version': 1,
    'disable_existing_loggers': False})
