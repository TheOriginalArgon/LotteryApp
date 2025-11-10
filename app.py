import logging
from flask import Flask, render_template, redirect, url_for, request, flash
from models import db, Draw
from scraping import scrape_fifa_rankings, scrape_quini_numbers
from apscheduler.schedulers.background import BackgroundScheduler
from collections import defaultdict
import atexit

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lottery_fifa.db'
db.init_app(app)

# Fetch FIFA rankings and Quini6 draws
fifa_ranking = scrape_fifa_rankings()
quini_draws, quini_draw_date = scrape_quini_numbers()

# Map draw numbers to FIFA rankings
def map_draw_to_ranking(draw, ranking):
    return [ranking[number] for number in draw]

@app.route('/')
def index():
    # Map current draws to FIFA rankings
    current_draws_mapped = [map_draw_to_ranking(draw, fifa_ranking) for draw in quini_draws]

    # Fetch previous draws from the database
    previous_draws = Draw.query.all()

    # Group previous draws by month and year
    grouped_draws = defaultdict(list)
    for draw in previous_draws:
        month_year = draw.draw_date.strftime('%B %Y')
        grouped_draws[month_year].append(draw)

    # Get selected month from the dropdown
    selected_month = request.args.get('month', default=None)

    # Filter draws for the selected month
    filtered_draws = grouped_draws[selected_month] if selected_month else []

    # Pass the top 46 countries to the template
    top_countries = [{'number': i + 1, 'team': fifa_ranking[i]['team']} for i in range(46)]

    # --- New logic for most frequent countries per set in last five draws ---
    last_five_draws = Draw.query.order_by(Draw.draw_date_rolled.desc()).limit(5).all()
    set_country_counts = [defaultdict(lambda: {'count': 0, 'flag': None}) for _ in range(4)]
    for draw in last_five_draws:
        for i, draw_set in enumerate([draw.draw_set_1, draw.draw_set_2, draw.draw_set_3, draw.draw_set_4]):
            for entry in draw_set:
                if isinstance(entry, dict):
                    country = entry.get('team', str(entry))
                    flag = entry.get('flag', None)
                else:
                    country = str(entry)
                    flag = None
                set_country_counts[i][country]['count'] += 1
                if flag:
                    set_country_counts[i][country]['flag'] = flag
    # Prepare sorted lists for each set
    most_frequent_countries_per_set = []
    for set_count in set_country_counts:
        sorted_countries = sorted(set_count.items(), key=lambda x: x[1]['count'], reverse=True)
        most_frequent = [
            {'team': team, 'count': data['count'], 'flag': data['flag']} for team, data in sorted_countries
        ]
        most_frequent_countries_per_set.append(most_frequent)

    # Render the index page with current and previous draws and frequent countries per set
    return render_template(
        'index.html',
        current_draws_mapped=current_draws_mapped,
        grouped_draws=grouped_draws,
        filtered_draws=filtered_draws,
        selected_month=selected_month,
        top_countries=top_countries,
        most_frequent_countries_per_set=most_frequent_countries_per_set
    )

def perform_save_draw():
    try:
        # Get the most recent draws
        most_recent_draws = quini_draws

        # Fetch the last saved draw from the database
        last_saved_draw = Draw.query.order_by(Draw.draw_date_rolled.desc()).first()

        # Save the draw if it's new
        if last_saved_draw is None or quini_draw_date > last_saved_draw.draw_date_rolled.date():
            draw_sets = [
                [{'team': team['team'], 'flag': team['flag'], 'number': most_recent_draws[i][j]} 
                 for j, team in enumerate(map_draw_to_ranking(most_recent_draws[i], fifa_ranking))]
                for i in range(4)
            ]

            draw_entry = Draw(
                draw_set_1=draw_sets[0],
                draw_set_2=draw_sets[1],
                draw_set_3=draw_sets[2],
                draw_set_4=draw_sets[3],
                draw_date_rolled=quini_draw_date
            )

            db.session.add(draw_entry)
            db.session.commit()
            logger.info("Draw saved successfully.")
        else:
            logger.info("No new draw to save. The latest draw is already up-to-date.")
    except Exception as e:
        logger.error("Error saving draw: %s", e)

@app.route('/save_draw', methods=['POST'])
def save_draw():
    # Save the most recent draw and redirect to the index page
    perform_save_draw()
    return redirect(url_for('index'))

@app.route('/simulate_draw', methods=['GET', 'POST'])
def simulate_draw():
    simulated_draw = []
    simulated_numbers = []
    error = None
    mode = request.form.get('mode', 'numbers') if request.method == 'POST' else 'numbers'
    if request.method == 'POST':
        try:
            if mode == 'numbers':
                numbers_str = request.form.get('set_1', '')
                numbers = [int(num.strip()) for num in numbers_str.split(',') if num.strip()]
                if len(numbers) != 6:
                    raise ValueError("Please enter exactly 6 numbers.")
                if not all(0 <= num < len(fifa_ranking) for num in numbers):
                    raise ValueError("Numbers must be between 0 and {}".format(len(fifa_ranking) - 1))
                simulated_draw = [fifa_ranking[number] for number in numbers]
            elif mode == 'flags':
                selected_teams = request.form.getlist('flag_team')
                if len(selected_teams) != 6:
                    raise ValueError("Please select exactly 6 teams.")
                # Find the zero-based number for each selected team
                for team_name in selected_teams:
                    for idx, team in enumerate(fifa_ranking):
                        if team['team'] == team_name:
                            simulated_numbers.append(idx)
                            break
                    else:
                        raise ValueError(f"Team '{team_name}' not found in ranking.")
        except Exception as e:
            error = str(e)
    top_countries = [{'number': i, 'team': fifa_ranking[i]['team']} for i in range(46)]
    return render_template(
        'simulate_draw.html',
        simulated_draw=simulated_draw,
        simulated_numbers=simulated_numbers,
        top_countries=top_countries,
        fifa_ranking=fifa_ranking,
        error=error,
        mode=mode
    )

# === MAIN EXECUTION ===
if __name__ == "__main__":
    app.run(debug=True)