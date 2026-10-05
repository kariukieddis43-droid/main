import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-this'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///prof_amon.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max upload size: 16 MB

ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx'}

db = SQLAlchemy(app)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# Database Model
class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    university = db.Column(db.String(100), nullable=False)
    course = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Document {self.title}>'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Routes
@app.route('/')
def index():
    search_query = request.args.get('q', '')
    if search_query:
        documents = Document.query.filter(
            (Document.title.contains(search_query)) |
            (Document.university.contains(search_query)) |
            (Document.course.contains(search_query))
        ).all()
    else:
        documents = Document.query.all()
    return render_template('index.html', documents=documents, query=search_query)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        title = request.form.get('title')
        university = request.form.get('university')
        course = request.form.get('course')
        description = request.form.get('description')
        file = request.files.get('file')

        if not file or file.filename == '':
            flash('No file selected!', 'danger')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            base, ext = os.path.splitext(filename)
            counter = 1
            unique_filename = filename
            while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)):
                unique_filename = f"{base}_{counter}{ext}"
                counter += 1

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))

            doc = Document(
                title=title,
                university=university,
                course=course,
                filename=unique_filename,
                description=description
            )
            db.session.add(doc)
            db.session.commit()

            flash('Document uploaded successfully to Prof Amon!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid file format. Allowed: PDF, TXT, DOC, DOCX', 'danger')

    return render_template('upload.html')


@app.route('/document/<int:doc_id>')
def view_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    return render_template('document.html', doc=doc)


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)