#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import http
import os
from flask import Flask, request
from werkzeug.wrappers import Response

from src.bot import *
app = Flask(__name__)


@app.route("/", methods=["POST"])
def index() -> Response:
    dispatcher.process_update(
      Update.de_json(request.get_json(force=True), bot))

    return "", http.HTTPStatus.NO_CONTENT


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))