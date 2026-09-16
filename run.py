"""
Author: Mourad.Soltani
Entry point for ResolveFabric P2P
"""
from backend.app import app
from backend.config import config

__author__ = "Mourad.Soltani"
__signature__ = "Mourad.Soltani"

if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT, debug=False)
