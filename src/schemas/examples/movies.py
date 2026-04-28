genre_schema_example = {"id": 1, "name": "Comedy"}

star_schema_example = {"id": 1, "name": "Leonardo Di Caprio"}

director_schema_example = {"id": 1, "name": "Christopher Nolan"}

genre_with_count_schema_example = {"id": 1, "name": "Comedy", "movies_count": 128}

movie_item_schema_example = {
    "id": 42,
    "uuid": "8be4df61-93ca-11d2-aa0d-00e098032b8c",
    "name": "The Swan Princess: A Royal Wedding",
    "year": 1999,
    "time": 180,
    "imdb": 5.2,
    "votes": 500,
    "meta_score": 80,
    "gross": 12000000.0,
    "price": 9.99,
}

movie_list_response_schema_example = {
    "movies": [movie_item_schema_example],
    "prev_page": "/theater/movies/?page=1&per_page=1",
    "next_page": "/theater/movies/?page=3&per_page=1",
    "total_pages": 9933,
    "total_items": 9933,
}

movie_create_schema_example = {
    "name": "New Movie",
    "year": 2025,
    "time": 120,
    "imdb": 7.8,
    "votes": 15000,
    "meta_score": 74,
    "gross": 5000000.0,
    "description": "An amazing movie.",
    "price": 12.99,
    "certification_id": 2,
    "genre_ids": [1, 3],
    "star_ids": [10, 11],
    "director_ids": [7],
}


movie_detail_schema_example = {
    **movie_item_schema_example,
    "description": "Princess Odette and Prince Derek are going to a wedding...",
    "certification_id": 2,
    "genres": [genre_schema_example],
    "stars": [star_schema_example],
    "directors": [director_schema_example],
}

movie_update_schema_example = {
    "name": "Update Movie",
    "imdb": 8.1,
    "price": 10.99,
    "genre_ids": [1, 2],
}

movie_vote_schema_example = {"is_liked": True}

movie_rating_schema_example = {"rating": 9}

movie_comment_create_schema_example = {
    "content": "This movie was better than I expected.",
    "parent_comment_id": None,
}

movie_comment_schema_example = {
    "id": 501,
    "movie_id": 42,
    "user_id": 7,
    "parent_comment_id": None,
    "content": "This movie was better than I expected.",
    "created_at": "2026-04-28T12:30:00Z",
    "updated_at": "2026-04-28T12:30:00Z",
}

movie_notification_schema_example = {
    "id": 1001,
    "recipient_user_id": 7,
    "sender_user_id": 12,
    "comment_id": 501,
    "event_type": "like",
    "is_read": False,
    "created_at": "2026-04-28T12:35:00Z",
}
