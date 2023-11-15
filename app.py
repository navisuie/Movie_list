from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.sql import func
import os
import traceback

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLACHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate  = Migrate(app,db)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = False)
    director = db.Column(db.String(100), nullable = False)
    imdb_rating = db.Column(db.Float , nullable = False)
    summary = db.Column(db.String(5000) , nullable = False)
    pub_date = db.Column(db.DateTime(timezone = True), server_default=func.now())

#route to enter a movie post
@app.route('/movie/create', methods = ['POST'])
def create_movie():
    try:
        movie_dict = {
            'title' : request.json['title'],
            'director' : request.json['director'],
            'imdb_rating' : request.json['imdb_rating'],
            'summary': request.json['summary']

        }
        new_movie = Movie(**movie_dict)
        db.session.add(new_movie)
        db.session.commit()
        movie_dict['id'] = new_movie.id
        movie_dict['pub_date'] = new_movie.pub_date
        return jsonify(movie_dict), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}),  400
    
#route to retrive all entered movie posts
@app.route('/movie/getall', methods = ['GET'])
def get_all():
    all_movies = Movie.query.all()
    movie_list = []
    for movie in all_movies:
        movie_list.append({
            'title': movie.title,
            'director': movie.director,
            'imdb_rating': movie.imdb_rating,
            'summary': movie.summary,
            'id': movie.id,
            'pub_date': movie.pub_date
        })
    return jsonify(movie_list)

#find a movie based on its title
@app.route('/movie/get/bytitle/<title>', methods=['GET'])
def get_by_title(title):
    check_all = Movie.query.filter(Movie.title.contains(title))
    if not len(list(check_all)):
        return jsonify({'error': 'no movies found with that title'}), 404
    movie_list = []
    for movie in check_all:
        movie_list.append({
            'title': movie.title,
            'director': movie.director,
            'imdb_rating': movie.imdb_rating,
            'summary': movie.summary,
            'id': movie.id,
            'pub_date': movie.pub_date
        })
    return jsonify(movie_list)

#update a movie post by title
@app.route('/movie/update/<id>', methods = ['PUT'])
def update_by_title(id):
    try:
        title = request.json['title']
        director = request.json['director']
        imdb_rating = request.json['imdb_rating']
        summary = request.json['summary']
        movie = Movie.query.get(id)
        if not movie:
            return jsonify({'error': 'there is no movie by this id'}), 404
        movie.title = title
        movie.director = director
        movie.imdb_rating = imdb_rating
        movie.summary = summary
        db.session.commit()
        movie_dict = {
            'title': movie.title,
            'director': movie.director,
            'imdb_rating': movie.imdb_rating,
            'summary': movie.summary,
            'id': movie.id,
            'pub_date': movie.pub_date
        }

        return jsonify(movie_dict)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

@app.route('/movie/delete/<id>', methods = ['DELETE'])
def delete_article(id):
    movie = Movie.query.get(id)
    if not movie:
        return jsonify({'error': 'there is no movie by this id'}), 404
    db.session.delete(movie)
    db.session.commit()
    movie_dict = {
        'title': movie.title,
        'director': movie.director,
        'imdb_rating': movie.imdb_rating,
        'summary': movie.summary,
        'id': movie.id,
        'pub_date': movie.pub_date
    }
    return jsonify(movie_dict)

if __name__ == '__main__':
    app.run(debug =True, port = 5000)


