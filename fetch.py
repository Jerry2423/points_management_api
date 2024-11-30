from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configure the SQLite database
db_name = 'transactions.db'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Define the Transaction model
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    payer = db.Column(db.String(50), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    # Points that have not been spent
    unspent_points = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'{self.payer} - {self.points} - {self.unspent_points} - {self.timestamp}'

# Define a route for the welcome message
@app.route('/')
def welcome():
    return 'Welcome to the Points Tracker!'


@app.route('/transactions')
def get_transactions():
    transactions = Transaction.query.all()
    output = []
    for transaction in transactions:
        transaction_data = {
            "payer": transaction.payer,
            "points": transaction.points,
            "unspent_points": transaction.unspent_points,
            "timestamp": transaction.timestamp
        }
        output.append(transaction_data)
    return jsonify({"transactions": output})


@app.route('/add', methods=['POST'])
def add_points():
    data = request.get_json()

    # Validate request data
    if not all(key in data for key in ('payer', 'points', 'timestamp')):
        return jsonify({"error": "Invalid request body"}), 400

    try:
        timestamp = datetime.fromisoformat(
            data['timestamp'].replace("Z", "+00:00"))
    except ValueError:
        return jsonify({"error": "Invalid timestamp format"}), 400

    if data['points'] < 0:
        try:
            deduct_point(abs(data['points']))
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    transaction = Transaction(
        payer=data['payer'],
        points=data['points'],
        # Edge case: unspent points cannot be negative
        unspent_points=max(0, data['points']),
        timestamp=timestamp
    )
    db.session.add(transaction)
    db.session.commit()

    return '', 200


@app.route('/spend', methods=['POST'])
def spend_points():
    data = request.get_json()

    # Validate the request body
    if 'points' not in data or not isinstance(data['points'], int):
        return "Invalid request body", 400

    points_to_spend = data['points']
    try:
        spent_points = deduct_point(points_to_spend)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(spent_points), 200


def deduct_point(points_to_spend):
    """
    Deducts points from transactions in the database, spending the oldest points first.

    Args:
        points_to_spend (int): The number of points to spend.

    Raises:
        ValueError: If the points_to_spend is negative or if there are insufficient points available.

    Returns:
        list: A list of dictionaries, each containing the payer and the points deducted.
    """
    if (points_to_spend < 0):
        raise ValueError("Invalid points")

    total_available_points = db.session.query(
        db.func.sum(Transaction.unspent_points)).scalar()

    # Check if the user has enough points
    if points_to_spend > total_available_points:
        raise ValueError("Insufficient points")

    # Spend points (oldest first)
    transactions = Transaction.query.filter(
        Transaction.unspent_points > 0).order_by(Transaction.timestamp).all()
    spent_points = []
    for transaction in transactions:
        if points_to_spend == 0:
            break

        # Determine points to deduct from this transaction
        spend_amount = min(transaction.unspent_points, points_to_spend)
        transaction.unspent_points -= spend_amount
        db.session.add(transaction)

        # Record the points spent
        payer_entry = next(
            (entry for entry in spent_points if entry['payer'] == transaction.payer), None)
        if payer_entry:
            payer_entry['points'] -= spend_amount
        else:
            spent_points.append(
                {"payer": transaction.payer, "points": -spend_amount})

        points_to_spend -= spend_amount

    db.session.commit()
    return spent_points


@app.route('/balance', methods=['GET'])
def get_balance():
    # Query the database to calculate the balance for each payer
    balances = db.session.query(
        Transaction.payer,
        db.func.sum(Transaction.unspent_points).label('balance')
    ).group_by(Transaction.payer).all()

    response = {payer: balance for payer, balance in balances}

    return jsonify(response), 200


if __name__ == "__main__":
    app.run(port=8000)
