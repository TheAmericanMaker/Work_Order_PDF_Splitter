import os
import sys
from importlib import import_module
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

create_app = import_module("work_order_splitter.web").create_app


app = create_app()


def main() -> None:
    debug = os.environ.get("FLASK_ENV", "").lower() == "development"
    app.run(debug=debug)


if __name__ == "__main__":
    main()
