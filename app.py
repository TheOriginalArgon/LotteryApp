from flask import Flask, render_template, redirect, url_for
from models import db, Draw
from scraping import scrape_fifa_rankings, scrape_quini_numbers

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lottery_fifa.db'
db.init_app(app)

# List containing top 46 teams and their flags.
fifa_ranking = scrape_fifa_rankings()

# List of arrays of the 4 draws.
quini_draws = scrape_quini_numbers()

# returns an array of tuples containing team and flag, alongside number.
def map_draw_to_ranking(draw, ranking):
    result = []
    for number in draw:
        result.append(ranking[number])
    return result

@app.route('/')
def index():

    current_draws_mapped = []
    for draw in quini_draws:
        current_draw_mapped = map_draw_to_ranking(draw, fifa_ranking)
        current_draws_mapped.append(current_draw_mapped)

    # Fetch the draws from the database.
    previous_draws = Draw.query.all()

    return render_template('index.html', current_draws_mapped = current_draws_mapped, previous_draws = previous_draws)

@app.route('/save_draw', methods = ['POST'])
def save_draw():

    most_recent_draws = quini_draws

    draw_1 = map_draw_to_ranking(most_recent_draws[0], fifa_ranking)
    draw_2 = map_draw_to_ranking(most_recent_draws[1], fifa_ranking)
    draw_3 = map_draw_to_ranking(most_recent_draws[2], fifa_ranking)
    draw_4 = map_draw_to_ranking(most_recent_draws[3], fifa_ranking)

    # Store as JSON objects.
    draw_entry = Draw(
        draw_set_1 = [{'team' : team['team'], 'flag' : team['flag'], 'number' : most_recent_draws[0][i]} for i, team in enumerate(draw_1)],
        draw_set_2 = [{'team' : team['team'], 'flag' : team['flag'], 'number' : most_recent_draws[1][i]} for i, team in enumerate(draw_2)],
        draw_set_3 = [{'team' : team['team'], 'flag' : team['flag'], 'number' : most_recent_draws[2][i]} for i, team in enumerate(draw_3)],
        draw_set_4 = [{'team' : team['team'], 'flag' : team['flag'], 'number' : most_recent_draws[3][i]} for i, team in enumerate(draw_4)]
    )

    # Save to database
    db.session.add(draw_entry)
    db.session.commit()

    return redirect(url_for('index'))


# === MAIN EXECUTION ===
if __name__ == "__main__":
    # for draw in quini_draws:
    #     draw_flags = map_draw_to_ranking(draw, fifa_ranking)
    #     print(f"Draw: {draw} -> Ranking: {draw_flags}")
    app.run(debug = True)