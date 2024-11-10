from datetime import datetime

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    date_modified = db.Column(db.DateTime, nullable=False, default=datetime.now)
    username = db.Column(db.String(24), nullable=False, unique=True)

    posts = db.relationship('Post', foreign_keys="Post.author_id", back_populates="author", lazy=True)
    replies = db.relationship("Reply", foreign_keys="Reply.author_id", back_populates="author", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "date_created": self.date_created.strftime("%m-%d-%Y $H:%M"),
            "date_modified": self.date_created.strftime("%m-%d-%Y $H:%M"),
            "username": self.username
        }

class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    date_modified = db.Column(db.DateTime, nullable=False, default=datetime.now)
    title = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    author = db.relationship("User", foreign_keys=[author_id], back_populates="posts", uselist=False,  lazy=True)
    replies = db.relationship("Reply", foreign_keys="Reply.post_id", back_populates="post", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "date_created": self.date_created.strftime("%m-%d-%Y $H:%M"),
            "date_modified": self.date_created.strftime("%m-%d-%Y $H:%M"),
            "title": self.title,
            "body": self.body
        }

class Reply(db.Model):
    __tablename__ = "replies"

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    date_modified = db.Column(db.DateTime, nullable=False, default=datetime.now)
    message = db.Column(db.Text, nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    author = db.relationship("User", foreign_keys=[author_id], back_populates="replies", uselist=False, lazy=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)
    post = db.relationship("Post", foreign_keys=[post_id], back_populates="replies", uselist=False, lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "date_created": self.date_created.strftime("%m-%d-%Y $H:%M"),
            "date_modified": self.date_created.strftime("%m-%d-%Y $H:%M"),
            "message": self.message
        }
    
with app.app_context():
    db.create_all()

@app.route("/ping", methods=["GET"])
def hello_world():
    return jsonify({"message": "Hello world!"}), 200

@app.route("/users", methods=["GET", "POST"])
def users_index():
    if request.method == "GET":
        users = User.query.all()
        return jsonify({"users": [u.to_dict() for u in users]}), 200
    if request.method == "POST":
        user = User(username=request.json.get("username"))
        db.session.add(user)
        db.session.commit()
        return jsonify({"user": user.to_dict()}), 200

@app.route("/users/<int:user_id>", methods=["GET", "PUT", "DELETE"])
def process_user(user_id):
    if request.method == "GET":
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found."}), 404
        
        return jsonify({"user": user.to_dict()}), 200
    if request.method == "PUT":
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found."}), 404
        
        for key, value in request.json:
            if not hasattr(user, key):
                return jsonify({"message": f"Invalid attribute: {key}"}), 400
            
            setattr(user, value)

        db.session.commit()
        return jsonify({"user": user.to_dict()}), 200
    if request.method == "DELETE":
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found."}), 404
        
        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": "User deleted."})

@app.route("/users/<int:user_id>/<field_name>", methods=["GET"])
def process_user_property(user_id, field_name):
    if request.method == "GET":
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found."}), 404
        
        if not hasattr(user, field_name):
            return jsonify({"message": f"Invalid attribute: {field_name}"}), 400
        
        prop = getattr(user, field_name)
        return jsonify({f"{field_name}": prop.to_dict()}), 200

@app.route("/posts", methods=["GET", "POST"])
def posts_index():
    if request.method == "GET":
        posts = Post.query.all()
        return jsonify({"posts": [p.to_dict() for p in posts]}), 200
    if request.method == "POST":
        post = Post(
            title=request.json.get("title"),
            body=request.json.get("body"),
            author_id=request.json.get("author_id"),
        )

        db.session.add(post)
        db.session.commit()

        return jsonify({"post": post.to_dict()}), 200

@app.route("/posts/<int:post_id>", methods=["GET", "PUT", "DELETE"])
def process_post(post_id):
    if request.method == "GET":
        post = Post.query.get(post_id)
        if not post:
            return jsonify({"message": "Post not found."}), 404
        
        return jsonify({"post": post.to_dict()}), 200
    if request.method == "PUT":
        post = Post.query.get(post_id)
        if not post:
            return jsonify({"message": "Post not found."}), 404
        
        for key, value in request.json:
            if not hasattr(post, key):
                return jsonify({"message": f"Invalid attribute: {key}"}), 400
            
            setattr(post, value)

        db.session.commit()
        
        return jsonify({"post": post.to_dict()}), 200
    if request.method == "DELETE":
        post = Post.query.get(post_id)
        if not post:
            return jsonify({"message": "Post not found."}), 404
        
        db.session.delete(post)
        db.session.commit()

        return jsonify({"message": "Post deleted."})

@app.route("/users/<int:post_id>/<field_name>", methods=["GET"])
def process_post_property(post_id, field_name):
    if request.method == "GET":
        post = Post.query.get(post_id)
        if not post:
            return jsonify({"message": "User not found."}), 404
        
        if not hasattr(post, field_name):
            return jsonify({"message": f"Invalid attribute: {field_name}"}), 400
        
        prop = getattr(post, field_name)
        return jsonify({f"{field_name}": prop.to_dict()}), 200

@app.route("/posts/<int:post_id>/replies", methods=["POST"])
def replies_index(post_id):
    if request.method == "POST":
        post = Post.query.get(post_id)
        if not post:
            return jsonify({"message": "Post not found."}), 404
        
        reply = Reply(
            message=request.json.get("message"),
            author_id=request.json.get("author_id"),
            post_id=post_id
        )

        db.session.add(reply)
        db.session.commit()
        return jsonify({"reply": reply.to_dict()}), 200

@app.route("/posts/<int:post_id>/replies/<int:reply_id>", methods=["GET", "PUT", "DELETE"])
def process_reply(post_id, reply_id):
    if request.method == "GET":
        post = Post.query.get(post_id)
        if not post:
            return jsonify({"message": "Post not found."}), 404
        
        reply = filter(lambda r: r.id == reply_id, post.replies).next()
        if not reply:
            return jsonify({"message": "Reply not found."}), 404

        return jsonify({"reply": reply.to_dict()}), 200
    if request.method == "PUT":
        post = Post.query.get(post_id)
        if not post:
            return jsonify({"message": "Post not found."}), 404
        
        reply = filter(lambda r: r.id == reply_id, post.replies).next()
        if not reply:
            return jsonify({"message": "Reply not found."}), 404
        
        for key, value in request.json:
            if not hasattr(reply, key):
                return jsonify({"message": f"Invalid attribute: {key}"}), 400
            
            setattr(reply, key, value)

        db.session.commit()
        return jsonify({"reply": reply.to_dict()}), 200
    if request.method == "DELETE":
        post = Post.query.get(post_id)
        if not post:
            return jsonify({"message": "Post not found."}), 404
        
        reply = filter(lambda r: r.id == reply_id, post.replies).next()
        if not reply:
            return jsonify({"message": "Reply not found."}), 404
        
        db.session.delete(reply)
        db.session.commit()

        return jsonify({"message": "Reply deleted"}), 200

@app.route("/posts/<int:post_id>/replies/<int:reply_id>/<field_name>", methods=["GET"])
def process_reply_property(post_id, reply_id, field_name):
    if request.method == "GET":
        post = Post.query.get(post_id)
        if not post:
            return jsonify({"message": "Post not found."}), 404
        
        reply = filter(lambda r: r.id == reply_id, post.replies).next()
        if not reply:
            return jsonify({"message": "Reply not found."}), 404
        
        if not hasattr(reply, field_name):
            return jsonify({"message": f"Invalid attribute: {field_name}"}), 400
        
        prop = getattr(reply, field_name)

        return jsonify({f"{field_name}": prop.to_dict()}), 200

if __name__ == "__main__":
    app.run(debug=True)
