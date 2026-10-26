from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Vinith@0998",
    "database": "test"
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


@app.route('/')
def dashboard():

    search = request.args.get('search', '')
    gender = request.args.get('gender', '')

    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Dashboard Stats
    cursor.execute("SELECT COUNT(*) total FROM test.voters")
    total_voters = cursor.fetchone()['total']

    cursor.execute(
        "SELECT COUNT(*) male FROM test.voters WHERE gender='Male'"
    )
    total_male = cursor.fetchone()['male']

    cursor.execute(
        "SELECT COUNT(*) female FROM test.voters WHERE gender='Female'"
    )
    total_female = cursor.fetchone()['female']

    cursor.execute(
        "SELECT ROUND(AVG(age),1) avg_age FROM test.voters"
    )
    avg_age = cursor.fetchone()['avg_age']

    # Search Query
    query = """
        SELECT *
        FROM test.voters
        WHERE 1=1
    """

    params = []

    if search:
        query += """
            AND (
                name LIKE %s
                OR epic_no LIKE %s
            )
        """

        params.extend([
            f'%{search}%',
            f'%{search}%'
        ])

    if gender:
        query += " AND gender=%s "
        params.append(gender)

    count_query = query.replace(
        "SELECT *",
        "SELECT COUNT(*) total"
    )

    cursor.execute(count_query, params)

    total_filtered = cursor.fetchone()['total']

    query += " LIMIT %s OFFSET %s"

    params.extend([per_page, offset])

    cursor.execute(query, params)

    voters = cursor.fetchall()

    cursor.execute("""
        SELECT gender,
               COUNT(*) count
        FROM test.voters
        GROUP BY gender
    """)

    gender_data = cursor.fetchall()

    cursor.close()
    conn.close()

    total_pages = (
        total_filtered + per_page - 1
    ) // per_page

    return render_template(
        "index.html",
        voters=voters,
        total_voters=total_voters,
        total_male=total_male,
        total_female=total_female,
        avg_age=avg_age,
        search=search,
        gender=gender,
        page=page,
        total_pages=total_pages,
        gender_data=gender_data
    )


if __name__ == "__main__":
    app.run(debug=True)