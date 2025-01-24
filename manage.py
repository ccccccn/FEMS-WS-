#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from showcenter.apps import ShowcenterConfig

def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taosPro.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
    # # 检查是否启动 Uvicorn
    # if len(sys.argv) > 1 and sys.argv[1] == "runuvicorn":
    #     import subprocess
    #     host = "192.168.102.75"
    #     port = "10000"
    #     reload = "--reload" if "--reload" in sys.argv else ""
    #     command = f"uvicorn taosPro.asgi:application --host {host} --port {port} {reload}"
    #     subprocess.run(command, shell=True)
    # else:
    #     execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
