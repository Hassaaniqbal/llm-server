from flask import Flask, request
from dotenv import load_dotenv, dotenv_values
from flask_cors import CORS, cross_origin

from controllers.interview import generate_interview_results

load_dotenv()

config = dotenv_values(".env")

app = Flask(__name__)
CORS(app)

@app.route("/interview", methods=["POST"])
@cross_origin()
def generate_results():
    post_data = request.json
    provider_id = post_data["provider_id"]

    return generate_interview_results(provider_id)


if __name__ == "__main__":
    app.run(host=config["HOST_NAME"], port=int(config["PORT_NUMBER"]))
