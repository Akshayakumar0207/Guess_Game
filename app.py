from flask import Flask, render_template, request, jsonify
import random, string

app = Flask(__name__)

rounds = {
    1: {"points": 10, "q": [
        ("Animal with long tail", "tiger"),
        ("King of jungle", "lion"),
        ("Yellow fruit", "banana"),
        ("Domestic animal", "dog"),
        ("Red fruit", "apple")
    ]},
    2: {"points": 20, "q": [
        ("Fastest land animal", "cheetah"),
        ("Tallest animal", "giraffe"),
        ("Animal with trunk", "elephant"),
        ("Pet bird", "parrot"),
        ("Striped animal", "zebra")
    ]},
    3: {"points": 30, "q": [
        ("Largest ocean animal", "blue whale"),
        ("Animal with pouch", "kangaroo"),
        ("Nocturnal bird", "owl"),
        ("Animal that laughs", "hyena"),
        ("Animal with horns", "rhino")
    ]},
    4: {"points": 40, "q": [
        ("Fastest bird", "falcon"),
        ("Animal that changes color", "chameleon"),
        ("Animal with armor", "armadillo"),
        ("Animal with ink", "octopus"),
        ("Longest living animal", "tortoise")
    ]},
    5: {"points": 50, "q": [
        ("Mammal that lays eggs", "platypus"),
        ("Largest land carnivore", "polar bear"),
        ("Only flying mammal", "bat"),
        ("Animal that sleeps standing", "horse"),
        ("Largest nocturnal bird", "owl")
    ]}
}

rooms = {}

def make_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

@app.route("/")
def home():
    return render_template("join.html")

@app.route("/create")
def create():
    code = make_code()
    rooms[code] = {
        "players": 0,
        "round": 1,
        "q": 0,
        "answers": {},
        "score": 0,
        "started": False
    }
    return jsonify({"code": code})

@app.route("/join", methods=["POST"])
def join():
    code = request.json["code"]
    if code in rooms and rooms[code]["players"] < 2:
        rooms[code]["players"] += 1
        if rooms[code]["players"] == 2:
            rooms[code]["started"] = True
        return jsonify({"ok": True})
    return jsonify({"ok": False})

@app.route("/game")
def game():
    return render_template("game.html")

@app.route("/status/<code>")
def status(code):
    room = rooms.get(code)
    if not room:
        return jsonify({"error": True})
    return jsonify({
        "players": room["players"],
        "started": room["started"]
    })

@app.route("/question/<code>")
def question(code):
    room = rooms[code]

    if not room["started"]:
        return jsonify({"wait": True})

    if room["round"] > 5:
        return jsonify({"end": True, "score": room["score"]})

    hint = rounds[room["round"]]["q"][room["q"]][0]
    return jsonify({
        "round": room["round"],
        "question": room["q"] + 1,
        "hint": hint,
        "score": room["score"],
        "points": rounds[room["round"]]["points"]
    })

@app.route("/submit/<code>", methods=["POST"])
def submit(code):
    room = rooms[code]
    data = request.json

    room["answers"][data["player"]] = data["answer"].strip().lower()

    if len(room["answers"]) == 2:
        correct = rounds[room["round"]]["q"][room["q"]][1]
        answers = list(room["answers"].values())

        if answers[0] == answers[1] == correct:
            room["score"] += rounds[room["round"]]["points"]

        room["answers"] = {}
        room["q"] += 1

        if room["q"] == 5:
            room["q"] = 0
            room["round"] += 1

    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True)
